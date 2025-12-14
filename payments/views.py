from rest_framework import mixins, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from payments.models import Payment
from payments.serializers import PaymentSerializer


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
            queryset = queryset.filter(user=user)

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
