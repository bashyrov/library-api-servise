from decimal import Decimal
import stripe
from django.conf import settings
from borrowings.models import Borrowing
from payments.models import Payment

stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentService:

    @staticmethod
    def create_checkout_session(borrowing: Borrowing, payment: Payment, money_to_paid=Decimal(0)):
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
            success_url=(
                f"{settings.STRIPE_SUCCESS_URL}"
                "?session_id={CHECKOUT_SESSION_ID}"
            ),
            cancel_url=settings.STRIPE_CANCEL_URL,
            metadata={
                "payment_id": payment.id,
            },
        )
        return session

    @staticmethod
    def create_base_payment(borrowing):
        start_date = borrowing.borrow_date
        end_date = borrowing.expected_return_date
        price_per_day = borrowing.book.daily_fee
        duration = max( 1, (end_date - start_date).days)
        amount = Decimal(price_per_day * duration)

        payment = Payment.objects.create(
            status=Payment.StatusChoices.PENDING,
            type=Payment.TypeChoices.PAYMENT,
            borrowing=borrowing,
            money_to_paid=amount,
        )

        payment_session = PaymentService.create_checkout_session(borrowing=borrowing, payment=payment, money_to_paid=amount)

        payment.session_url = payment_session.url
        payment.session_id = payment_session.id
        payment.save(update_fields=['session_url', 'session_id'])

        return payment

    @staticmethod
    def create_fine_payment(borrowing: Borrowing) -> Payment:
        if borrowing.actual_return_date:
            overdue_days = max(
                1,
                (borrowing.actual_return_date - borrowing.expected_return_date).days
            )

            if overdue_days > 0:
                price_per_day = borrowing.book.daily_fee
                amount = Decimal(price_per_day * overdue_days)

                fine = Payment.objects.create(
                    status=Payment.StatusChoices.PENDING,
                    type=Payment.TypeChoices.FINE,
                    borrowing=borrowing,
                    money_to_paid=amount,
                )

                payment_session = PaymentService.create_checkout_session(borrowing=borrowing, payment=fine, money_to_paid=amount)

                fine.session_url = payment_session.url
                fine.session_id = payment_session.id
                fine.save(update_fields=['session_url', 'session_id'])

                return fine
