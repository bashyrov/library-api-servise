from datetime import date

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.reverse import reverse
from books.models import Book

BORROWINGS_URL = reverse("borrowings:borrowings-list-create")


def sample_book():
    return Book.objects.create(
        title="Book 1",
        author="<NAME>",
        cover="SOFT",
        inventory=5,
        daily_fee=1.99,
    )


class UnauthenticatedBorrowingsTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_borrowings_list_queryset(self):
        ...

    def test_unauthenticated_borrowings(self):
        ...


class BorrowingsTechTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_decrease_inventory(self): #TODO: Add user to payload

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