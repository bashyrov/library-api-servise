from decimal import Decimal

from django.db import models

from borrowings.models import Borrowing


class Payment(models.Model):

    class StatusChoices(models.TextChoices):
        PENDING = "Pending"
        PAID = "Paid"

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
    session_url = models.URLField(null=True, blank=True)
    session_id = models.CharField(null=True, blank=True, max_length=255)
    money_to_paid = models.DecimalField(decimal_places=2, max_digits=10)


