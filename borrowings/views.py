from django.db import transaction
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (OpenApiExample,
                                   extend_schema,
                                   OpenApiParameter)
from rest_framework import status, mixins, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from borrowings.models import Borrowing
from borrowings.serializers import (BorrowingSerializer,
                                    BorrowingDetailSerializer)
from payments.services import PaymentService


class BorrowingViewSet(mixins.ListModelMixin,
                       mixins.CreateModelMixin,
                       mixins.RetrieveModelMixin,
                       viewsets.GenericViewSet,
                       ):
    serializer_class = BorrowingSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication, )

    def perform_create(self, serializer):
        with transaction.atomic():
            borrowing = serializer.save(
                user=self.request.user,
            )
            payment = PaymentService.create_base_payment(borrowing)

            self.extra_response_data = {
                "payment_session_url": payment.session_url}

    @extend_schema(
        summary="Create a borrowing",
        description=(
                "Create a new borrowing for the authenticated user.\n\n"
                "Rules:\n"
                "- Book must be available in inventory\n"
                "- Expected return date must be today or later\n\n"
                "Side effects:\n"
                "- Creates a payment session\n"
                "- Returns payment_session_url in response"
        ),
        request=BorrowingSerializer,
        responses={
            201: BorrowingSerializer,
            400: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
        },
        examples=[
            OpenApiExample(
                name="Successful creation",
                value={
                    "id": 1,
                    "borrow_date": "2025-12-18",
                    "expected_return_date": "2025-12-25",
                    "actual_return_date": None,
                    "book": 3,
                    "user": 5,
                    "payment_session_url": "https://checkout.stripe.com/..."
                },
                response_only=True,
                status_codes=["201"],
            ),
            OpenApiExample(
                name="No inventory",
                value={
                    "non_field_errors": [
                        "We don't have enough inventory."
                    ]
                },
                response_only=True,
                status_codes=["400"],
            ),
            OpenApiExample(
                name="Invalid return date",
                value={
                    "non_field_errors": [
                        "Please enter a valid date."
                    ]
                },
                response_only=True,
                status_codes=["400"],
            ),
        ],
    )
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)

        if hasattr(self, "extra_response_data"):
            response.data.update(self.extra_response_data)

        return response

    @extend_schema(
        summary="Return borrowed book",
        description=(
                "Marks the borrowing as returned.\n\n"
                "Rules:\n"
                "- Users can return only their own borrowings\n"
                "- If the borrowing is "
                "already returned, an error is returned\n"
                "- If the borrowing is overdue, "
                "a fine payment session is created\n\n"
                "Side effects:\n"
                "- Sets actual return date\n"
                "- Increases book inventory\n"
                "- Creates fine payment if needed"
        ),
        responses={
            200: OpenApiTypes.OBJECT,
            400: OpenApiTypes.OBJECT,
            403: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
        examples=[
            OpenApiExample(
                name="Returned without fine",
                value={
                    "detail": "Returned successfully."
                },
                response_only=True,
                status_codes=["200"],
            ),
            OpenApiExample(
                name="Returned with fine",
                value={
                    "detail": "Returned successfully.",
                    "payments": "Please pay the fine.",
                    "payment_session_url": "https://checkout.stripe.com/..."
                },
                response_only=True,
                status_codes=["200"],
            ),
            OpenApiExample(
                name="Already returned",
                value={
                    "detail": "Already returned."
                },
                response_only=True,
                status_codes=["400"],
            ),
            OpenApiExample(
                name="Permission denied",
                value={
                    "detail": "You don't have permission to do this."
                },
                response_only=True,
                status_codes=["403"],
            ),
        ],
    )
    @action(detail=True, methods=["post"], url_path="return")
    def return_borrowing(self, request, pk=None):
        borrowing_obj = self.get_object()

        if not borrowing_obj.user == self.request.user:
            return Response(
                {"detail": "You don't have permission to do this."},
                status=status.HTTP_403_FORBIDDEN
            )

        if borrowing_obj.actual_return_date:
            return Response(
                {"detail": "Already returned."},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            borrowing_obj.set_actual_return_date()
            book_obj = borrowing_obj.book
            book_obj.inventory += 1
            book_obj.save()
            payment_fine = PaymentService.create_fine_payment(borrowing_obj)

        message = {
            "detail": "Returned successfully.",
        }

        if payment_fine:
            message["payments"] = "Please pay the fine."
            message["payment_session_url"] = payment_fine.session_url

        return Response(message, status=status.HTTP_200_OK)

    def get_queryset(self):
        user = self.request.user
        is_user_admin = user.is_superuser or user.is_staff
        queryset = Borrowing.objects.all()

        if not is_user_admin:
            queryset = queryset.filter(user=user)

        is_active = self.request.query_params.get("is_active")
        user_pk = self.request.query_params.get("user_id")

        if is_active is not None:
            is_active = is_active.lower() == "true"
            if is_active:
                queryset = queryset.filter(actual_return_date__isnull=True)
            else:
                queryset = queryset.filter(actual_return_date__isnull=False)

        if user_pk:
            if not is_user_admin:
                raise PermissionDenied(
                    {
                        "detail":
                            "You don't have permission to view this borrowing."
                    }
                )
            user_pk = int(user_pk)
            try:
                queryset = queryset.filter(user__pk=user_pk)
            except Exception as e:
                raise ValueError(
                    {"detail": f"{e}"}
                )

        return queryset

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BorrowingDetailSerializer
        return BorrowingSerializer

    @extend_schema(
        summary="Retrieve borrowing",
        description=(
                "Retrieve detailed information about a borrowing.\n\n"
                "Permissions:\n"
                "- Regular users can access only their own borrowings\n"
                "- Admin users can access any borrowing"
        ),
        responses={
            200: BorrowingDetailSerializer,
            403: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
        examples=[
            OpenApiExample(
                name="Successful response",
                value={
                    "id": 1,
                    "borrow_date": "2025-12-18",
                    "expected_return_date": "2025-12-25",
                    "actual_return_date": None,
                    "book": {
                        "id": 3,
                        "title": "Clean Code",
                        "author": "Robert C. Martin"
                    },
                    "user": 5
                },
                response_only=True,
                status_codes=["200"],
            ),
            OpenApiExample(
                name="Permission denied",
                value={
                    "detail":
                        "You do not have permission to perform this action."
                },
                response_only=True,
                status_codes=["403"],
            ),
        ],
    )
    def retrieve(self, request, *args, **kwargs):
        borrowing_obj = self.get_object()

        if not borrowing_obj.user == self.request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(borrowing_obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Get list of borrowings",
        description=(
                "Returns a list of borrowings.\n\n"
                "- Regular users see only their own borrowings\n"
                "- Admin users can see all borrowings\n\n"
                "Filters:\n"
                "- **is_active=true** → only active borrowings\n"
                "- **is_active=false** → only returned borrowings\n"
                "- **user_id** → filter by user (admin only)"
        ),
        parameters=[
            OpenApiParameter(
                name="is_active",
                type=OpenApiTypes.BOOL,
                required=False,
                description="Filter by active status (true / false)",
            ),
            OpenApiParameter(
                name="user_id",
                type=OpenApiTypes.INT,
                required=False,
                description="Filter by user ID (admin only)",
            ),
        ],
        responses={
            200: BorrowingSerializer(many=True),
            403: OpenApiTypes.OBJECT,
        },
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
