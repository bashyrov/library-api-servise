from decimal import Decimal
import stripe
from borrowings.models import Borrowing
from payments.models import Payment


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
                    'unit_amount': money_to_paid * 100,
                },
                'quantity': 1,
            }],
            mode='payment',
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
    def create_fine_payment(borrowing: Borrowing, overdue_days: int) -> Payment:
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

    @staticmethod
    def create_payments(borrowing: Borrowing):
        base_payment = PaymentService.create_base_payment(borrowing)
        fine_payment = None

        if borrowing.actual_return_date:
            overdue_days = (
                    borrowing.actual_return_date - borrowing.expected_return_date
            ).days

            if overdue_days > 0:
                fine_payment = PaymentService.create_fine_payment(borrowing, overdue_days)

        return {
            "base_payment": base_payment,
            "fine_payment": fine_payment,
        }
