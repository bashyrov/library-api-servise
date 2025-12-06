from django.urls import path

from borrowings.views import BorrowingGeneric

app_name = 'borrowings'

urlpatterns = [
    path("", BorrowingGeneric.as_view(), name="borrowings-list-create"),
    path("<int:pk>/", BorrowingGeneric.as_view(), name="borrowings-retrieve"),
]



