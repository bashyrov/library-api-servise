from celery import shared_task
from tg_notifications.services.telegram import send_message


@shared_task
def notify_admins(text):
    send_message(text)