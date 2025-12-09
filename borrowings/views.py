from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from borrowings.models import Borrowing
from borrowings.serializers import BorrowingSerializer


class BorrowingGeneric(generics.ListCreateAPIView):
    serializer_class = BorrowingSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        if not instance.user == self.request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

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
                raise ValidationError(
                    {"user_id": "You don't have a permission to view this endpoint."}
                )
            user_pk = int(user_pk)
            try:
                queryset = queryset.filter(user__pk=user_pk)
            except Exception as e:
                raise ValueError(
                    {"user_id": f"{e}"}
                )

        return queryset

