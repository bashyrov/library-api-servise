from datetime import date
from http.client import responses

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.reverse import reverse
from books.models import Book
from borrowings.models import Borrowing
from borrowings.serializers import BorrowingSerializer

BORROWINGS_URL = reverse("borrowings:borrowings-list")

user_model = get_user_model()


def sample_book():
    return Book.objects.create(
        title="Book 1",
        author="<NAME>",
        cover="SOFT",
        inventory=5,
        daily_fee=1.99,
    )


def sample_borrowing(client:  user_model, book: Book = None):
    if book is None:
        book = sample_book()

    return Borrowing.objects.create(
        expected_return_date=date.today(),
        book=book,
        user=client,
    )


class UnauthenticatedBorrowingsTest(TestCase):
    def setUp(self):

        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(BORROWINGS_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBorrowingsTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = user_model.objects.create_user(
            email="test_user@example.com",
            password="password",
        )
        self.client.force_authenticate(self.user)

    def test_borrowings_auth_success(self):
        response = self.client.get(BORROWINGS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_decrease_inventory(self):

        book_obj = sample_book()
        payload = {
            "expected_return_date": str(date.today()),
            "book": book_obj.pk,
        }

        response = self.client.post(
            BORROWINGS_URL,
            payload,
            format="json"
        )

        book = Book.objects.get(pk=book_obj.pk)

        self.assertEqual(book.inventory, book_obj.inventory - 1)

    def test_borrowings_queryset(self):
        sample_borrowing(client=self.user)
        book_obj_returned = sample_borrowing(client=self.user)

        book_obj_returned.actual_return_date = date.today()
        book_obj_returned.save()

        response = self.client.get(
            BORROWINGS_URL,
            {
                "is_active": True,
            }
        )

        users_borrowings = Borrowing.objects.filter(
            user=self.user,
            actual_return_date__isnull=True
        )
        serializers = BorrowingSerializer(users_borrowings, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializers.data)

    def test_user_id_filter_unauthorized(self):
        sample_borrowing(client=self.user)

        self.user_test = user_model.objects.create_user(
            email="admi1@admin.com",
            password="password",
            is_staff=True,
        )

        response = self.client.get(
            BORROWINGS_URL,
            {
                "user_id": self.user_test.id,
            }
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["detail"], "You don't have permission to view this borrowing.")

    def test_return_book_increase_inventory(self):
        borrowings_obj = sample_borrowing(client=self.user)
        book_obj_before = borrowings_obj.book

        response = self.client.post(
            reverse("borrowings:borrowings-return-borrowing", args=[borrowings_obj.id])
        )

        book_obj_after = Book.objects.get(pk=book_obj_before.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "Returned successfully.")
        self.assertEqual(book_obj_after.inventory, book_obj_before.inventory + 1)


class AdminBorrowingsTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = user_model.objects.create_user(
            email="admin@admin.com",
            password="password",
            is_staff=True,
        )

        self.client.force_authenticate(self.user)

    def test_user_id_filter_success(self):
        sample_borrowing(client=self.user)

        self.user_test = user_model.objects.create_user(
            email="admi1@admin.com",
            password="password",
            is_staff=True,
        )

        response = self.client.get(
            BORROWINGS_URL,
            {
                "user_id": self.user_test.id,
            }
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)



