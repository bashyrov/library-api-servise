from decimal import Decimal

from django.db import models


class Book(models.Model):

    class CoverChoises(models.TextChoices):
        Hard = "Hard"
        SOFT = "Soft"

    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    cover = models.CharField(max_length=4, choices=CoverChoises)
    inventory = models.PositiveIntegerField(default=0)
    daily_fee = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal('0.00'))
