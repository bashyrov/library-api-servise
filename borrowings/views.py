from rest_framework import generics, status
from rest_framework.response import Response

from borrowings.models import Borrowing
from borrowings.serializers import BorrowingSerializer


class BorrowingGeneric(generics.ListCreateAPIView):
    queryset = Borrowing.objects.filter()
    serializer_class = BorrowingSerializer

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
        queryset = self.queryset.filter(user=self.request.user)

        return queryset

