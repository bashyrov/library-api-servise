from django.db.models.signals import post_save
from django.dispatch import receiver
from borrowings.models import Borrowing
from tg_notifications.tasks import send_telegram_notification
from payments.models import Payment


@receiver(post_save, sender=Borrowing)
def notify_borrowing_created(sender, instance, created, **kwargs):
    """
    Notify admins when a new borrowing is created
    """
    if not created:
        return

    send_telegram_notification.delay(
        f"📚 New borrowing created\n"
        f"User: {instance.user.email}\n"
        f"Book: {instance.book.title}\n"
        f"Return until: {instance.expected_return_date}"
    )


@receiver(post_save, sender=Payment)
def notify_payment_paid(sender, instance, created, **kwargs):
    """
    Notify admins when payment is successfully paid
    """
    if instance.status != Payment.StatusChoices.PAID:
        return

    send_telegram_notification.delay(
        f"💳 Payment successful\n"
        f"User: {instance.borrowing.user.email}\n"
        f"Amount: {instance.money_to_paid}\n"
        f"Type: {instance.type}"
    )
