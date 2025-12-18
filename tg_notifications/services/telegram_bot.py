import requests
from telegram import Bot
from django.conf import settings

bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)


def send_message(text: str):
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    chat_id = settings.TELEGRAM_CHAT_ID
    try:
        response = requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=5)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to send message to {chat_id}: {e}")
