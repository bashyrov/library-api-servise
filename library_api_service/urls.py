from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/books/", include("books.urls", namespace="books")),
    path("api/borrowings/", include("borrowings.urls", namespace="borrowings")),
    path("api/users/", include("users.urls", namespace="users")),
]
