import datetime
from datetime import date, timedelta
import stripe
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.reverse import reverse
from borrowings.tests.tests_borrowings import (sample_book,
                                               BORROWINGS_URL,
                                               sample_borrowing)
from payments.models import Payment
from payments.serializers import PaymentSerializer

PAYMENTS_URL = reverse("payments:payments-list")

user_model = get_user_model()
stripe.api_key = settings.STRIPE_SECRET_KEY


def sample_payment(client: user_model):
    borrowing = sample_borrowing(client=client)

    return Payment.objects.create(
        type=Payment.TypeChoices.FINE,
        status=Payment.StatusChoices.PENDING,
        borrowing=borrowing,
        money_to_paid=100
    )


class UnauthenticatedPaymentsTest(TestCase):
    def setUp(self):

        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(PAYMENTS_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedPaymentsTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = user_model.objects.create_user(
            email="test_user@example.com",
            password="password",
        )
        self.client.force_authenticate(self.user)

    def test_borrowings_auth_success(self):
        response = self.client.get(PAYMENTS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_auto_creation_payment(self):

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

        self.assertIn("payment_session_url", response.data)

    def test_payments_queryset(self):
        sample_payment(client=self.user)

        response = self.client.get(PAYMENTS_URL)

        users_payments = Payment.objects.filter(
            borrowing__user=self.user,
        )
        serializers = PaymentSerializer(users_payments, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializers.data)

    def test_fine_fee_calculation(self):
        book_obj = sample_book()
        borrowing = sample_borrowing(client=self.user)

        borrowing.borrow_date = date.today() - timedelta(days=15)
        borrowing.expected_return_date = date.today() - timedelta(days=10)
        borrowing.save()

        response = self.client.post(
            reverse(
                "borrowings:borrowings-return-borrowing",
                kwargs={
                    "pk": borrowing.id}),
            format="json")

        payment_session_url = response.data["payment_session_url"]
        session_id = payment_session_url.split("#")[0][34:]
        checkout_session = stripe.checkout.Session.retrieve(session_id)
        expected_amount_to_pay = checkout_session.amount_total / 100
        overdue_fee = book_obj.daily_fee * \
            (datetime.date.today() - borrowing.expected_return_date).days

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(overdue_fee, expected_amount_to_pay)

    def test_base_fee_calculation(self):
        book_obj = sample_book()
        borrowing = sample_borrowing(client=self.user)

        borrowing.borrow_date = date.today() - timedelta(days=5)
        borrowing.expected_return_date = date.today()
        borrowing.save()

        payload = {
            "expected_return_date": str(date.today() + timedelta(days=5)),
            "book": book_obj.pk,
        }

        response = self.client.post(
            BORROWINGS_URL,
            payload,
            format="json"
        )

        payment_session_url = response.data["payment_session_url"]
        session_id = payment_session_url.split("#")[0][34:]
        checkout_session = stripe.checkout.Session.retrieve(session_id)
        expected_amount_to_pay = checkout_session.amount_total / 100
        base_fee = book_obj.daily_fee * \
            (datetime.date.today() - borrowing.borrow_date).days

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(base_fee, expected_amount_to_pay)
