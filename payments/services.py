from decimal import Decimal

from payments.models import Payment


class PaymentService:

    @staticmethod
    def calculate_base_price(borrowing):
        start_date = borrowing.borrow_date
        end_date = borrowing.expected_return_date
        price_per_day = borrowing.book.daily_fee

        duration = (end_date - start_date).days

        amount = Decimal(price_per_day * duration)

        payment = Payment.objects.create(
            status=Payment.StatusChoices.PENDING,
            type=Payment.TypeChoices.PAYMENT,
            borrowing=borrowing,
            session_url="http://test_url",
            session_id="test_session_id",
            money_to_paid=amount,
        )
        return payment

    @staticmethod
    def calculate_fine(borrowing) -> Payment:

        if borrowing.actual_return_date:
            overdue_days = (
                    borrowing.actual_return_date - borrowing.expected_return_date
            ).days

            if overdue_days > 0:
                price_per_day = borrowing.book.daily_fee
                amount = Decimal(price_per_day * overdue_days)

                fine = Payment.objects.create(
                    status=Payment.StatusChoices.PENDING,
                    type=Payment.TypeChoices.FINE,
                    borrowing=borrowing,
                    session_url="http://test_url",
                    session_id="test_session_id",
                    money_to_paid=amount,
                )
                return fine
