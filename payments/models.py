from decimal import Decimal

from django.db import models

from borrowings.models import Borrowing


class Payment(models.Model):

    class StatusChoices(models.TextChoices):
        PENDING = "Pending"
        PAID =  "Paid"

    class TypeChoices(models.TextChoices):
        PAYMENT = "Payment"
        FINE = "Fine"

    status = models.CharField(
        max_length=10,
        choices=StatusChoices,
        default=StatusChoices.PENDING,
    )

    type = models.CharField(
        max_length=10,
        choices=TypeChoices,
    )

    borrowing = models.ForeignKey(Borrowing, on_delete=models.PROTECT, related_name="payments")
    session_url = models.URLField(null=False, blank=False)
    session_id = models.CharField(null=False, blank=False, max_length=255)
    money_to_paid = models.DecimalField(decimal_places=2, max_digits=10)

    def calculate_amount(self):

        if self.type == Payment.TypeChoices.PAYMENT:
            return self._calculate_base_price()
        elif self.type == Payment.TypeChoices.FINE:
            return self._calculate_fine()

    def _calculate_base_price(self):
        start_date = self.borrowing.borrow_date
        end_date = self.borrowing.expected_return_date
        price_per_day = self.borrowing.book.daily_fee

        duration = (end_date - start_date).days

        return price_per_day * duration

    def _calculate_fine(self):

        if not self.borrowing.actual_return_date:
            return Decimal("0.00")

        overdue_days = (
                self.borrowing.actual_return_date - self.borrowing.expected_return_date
        ).days

        if overdue_days <= 0:
            return Decimal("0.00")

        price_per_day = self.borrowing.book.daily_fee

        return price_per_day * overdue_days

