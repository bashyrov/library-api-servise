from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, permissions

from books.models import Book
from books.serializers import BooksSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BooksSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    @extend_schema(
        summary="Get list of books",
        description="Retrieve a list of all available books. Public access.",
        responses={
            200: BooksSerializer(many=True),
        },
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Retrieve book",
        description="Retrieve detailed information about a book. Public access.",
        responses={
            200: BooksSerializer,
            404: OpenApiTypes.OBJECT,
        },
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Create book",
        description="Create a new book. Admin access only.",
        request=BooksSerializer,
        responses={
            201: BooksSerializer,
            401: OpenApiTypes.OBJECT,
            403: OpenApiTypes.OBJECT,
        },
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        summary="Update book",
        description="Update book details. Admin access only.",
        request=BooksSerializer,
        responses={
            200: BooksSerializer,
            401: OpenApiTypes.OBJECT,
            403: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        summary="Partially update book",
        description="Partially update book details. Admin access only.",
        request=BooksSerializer,
        responses={
            200: BooksSerializer,
            401: OpenApiTypes.OBJECT,
            403: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        summary="Delete book",
        description="Delete a book. Admin access only.",
        responses={
            204: None,
            401: OpenApiTypes.OBJECT,
            403: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)