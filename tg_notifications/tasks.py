from celery import shared_task
from django.utils.timezone import now
from borrowings.models import Borrowing
from payments.models import Payment
from tg_notifications.services.telegram_bot import send_message


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={"max_retries": 3})
def send_telegram_notification(self, text: str):
    send_message(text)


@shared_task
def check_overdue_borrowings():
    overdue = Borrowing.objects.filter(expected_return_date__lt=now().date(), actual_return_date__isnull=True)
    for b in overdue:
        send_telegram_notification.delay(
            f"⚠️ Borrowing #{b.id} by {b.user.email} is overdue!"
        )


@shared_task
def daily_summary():
    today = now().date()
    borrowings_today = Borrowing.objects.filter(borrow_date=today).count()
    payments_today = Payment.objects.filter(status=Payment.StatusChoices.PAID)
    total_amount = sum(p.money_to_paid for p in payments_today)

    send_telegram_notification.delay(
        f"📊 Daily Summary ({today}):\n"
        f"New borrowings: {borrowings_today}\n"
        f"Payments: {payments_today.count()}\n"
        f"Total received: {total_amount}"
    )
