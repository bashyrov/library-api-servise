import stripe
from django.conf import settings
from rest_framework import mixins, viewsets, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from payments.models import Payment
from payments.serializers import PaymentSerializer


stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentViewSet(mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet
                     ):
    serializer_class = PaymentSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        is_user_admin = user.is_superuser or user.is_staff
        queryset = Payment.objects.all()

        if not is_user_admin:
            queryset = queryset.filter(borrowing__user=user)

        user_pk = self.request.query_params.get("user_id")
        type = self.request.query_params.get("type")

        if type:
            if type == "payment":
                queryset = queryset.filter(type=Payment.TypeChoices.PAYMENT)
            elif type == "fine":
                queryset = queryset.filter(type=Payment.TypeChoices.FINE)

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


class StripeSuccessAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        session_id = request.query_params.get("session_id")

        if not session_id:
            return Response(
                {"detail": "session_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            session = stripe.checkout.Session.retrieve(session_id)
        except stripe.error.InvalidRequestError:
            return Response(
                {"detail": "Invalid session_id"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if session.payment_status != "paid":
            return Response(
                {"detail": "Payment not completed"},
                status=status.HTTP_400_BAD_REQUEST
            )

        payment_id = session.metadata.get("payment_id")
        if not payment_id:
            return Response(
                {"detail": "payment_id not found"},
                status=status.HTTP_400_BAD_REQUEST
            )

        payment_obj = Payment.objects.get(id=payment_id)
        payment_obj.status = Payment.StatusChoices.PAID
        payment_obj.save(update_fields=['status'])

        customer = None
        if session.customer:
            customer = stripe.Customer.retrieve(session.customer)

        return Response(
            {
                "message": "Payment successful",
                "payment_id": payment_id,
                "amount_total": session.amount_total,
                "currency": session.currency,
                "customer": {
                    "name": customer.name if customer else None,
                    "email": customer.email if customer else None,
                },
            },
            status=status.HTTP_200_OK
        )



class StripePaymentCancelAPIView(APIView):
    """
    Called when Stripe Checkout is cancelled.
    """

    def get(self, request):
        return Response(
            {"detail": "Payment was cancelled. You can try again."},
            status=status.HTTP_200_OK
        )

