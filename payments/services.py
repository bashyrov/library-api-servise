from decimal import Decimal
import stripe
from django.conf import settings
from django.urls import reverse

from borrowings.models import Borrowing
from payments.models import Payment

stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentService:

    @staticmethod
    def create_checkout_session(borrowing: Borrowing, money_to_paid=Decimal(0)):
        session = stripe.checkout.Session.create(
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': borrowing.book.title,
                    },
                    'unit_amount': int(money_to_paid * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url="http://127.0.0.1:8000/api/payments/success",
            cancel_url="http://127.0.0.1:8000/api/payments/cancel"
        )
        return session

    @staticmethod
    def create_base_payment(borrowing):
        start_date = borrowing.borrow_date
        end_date = borrowing.expected_return_date
        price_per_day = borrowing.book.daily_fee
        duration = (end_date - start_date).days
        amount = Decimal(price_per_day * duration)

        payment_session = PaymentService.create_checkout_session(borrowing, amount)

        payment = Payment.objects.create(
            status=Payment.StatusChoices.PENDING,
            type=Payment.TypeChoices.PAYMENT,
            borrowing=borrowing,
            session_url=payment_session.url,
            session_id=payment_session.id,
            money_to_paid=amount,
        )
        return payment

    @staticmethod
    def create_fine_payment(borrowing: Borrowing) -> Payment:
        if borrowing.actual_return_date:
            overdue_days = (
                    borrowing.actual_return_date - borrowing.expected_return_date
            ).days

            if overdue_days > 0:
                price_per_day = borrowing.book.daily_fee
                amount = Decimal(price_per_day * overdue_days)

                payment_session = PaymentService.create_checkout_session(borrowing, amount)

                fine = Payment.objects.create(
                    status=Payment.StatusChoices.PENDING,
                    type=Payment.TypeChoices.FINE,
                    borrowing=borrowing,
                    session_url=payment_session.url,
                    session_id=payment_session.id,
                    money_to_paid=amount,
                )
                return fine
