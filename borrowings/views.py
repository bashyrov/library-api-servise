from django.db import transaction
from rest_framework import status, mixins, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from borrowings.models import Borrowing
from borrowings.serializers import BorrowingSerializer
from payments.services import PaymentService


class BorrowingViewSet(mixins.ListModelMixin,
                       mixins.CreateModelMixin,
                       mixins.RetrieveModelMixin,
                       viewsets.GenericViewSet,
                       ):
    serializer_class = BorrowingSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        with transaction.atomic():
            borrowing = serializer.save(
                user=self.request.user,
            )
            payment = PaymentService.create_base_payment(borrowing)

            self.extra_response_data = {"payment_session_url": payment.session_url}

    def retrieve(self, request, *args, **kwargs):
        borrowing_obj = self.get_object()

        if not borrowing_obj.user == self.request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(borrowing_obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)

        if hasattr(self, "extra_response_data"):
            response.data.update(self.extra_response_data)

        return response

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
                    {"detail": "You don't have permission to view this borrowing."}
                )
            user_pk = int(user_pk)
            try:
                queryset = queryset.filter(user__pk=user_pk)
            except Exception as e:
                raise ValueError(
                    {"detail": f"{e}"}
                )

        return queryset

