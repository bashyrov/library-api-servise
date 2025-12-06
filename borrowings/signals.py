from django.dispatch import receiver
from django.db.models.signals import post_save
from rest_framework.exceptions import ValidationError

from .models import Borrowing


@receiver(post_save, sender=Borrowing)
def borrowing_decrease_book_inventory(sender, instance, created, **kwargs):
    if not created:
        return

    book_obj = instance.book

    if book_obj.inventory <= 0:
        raise ValidationError("We don't have enough inventory")

    book_obj.inventory -= 1

    book_obj.save()