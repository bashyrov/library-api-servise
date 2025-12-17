from telegram import Bot
from django.conf import settings

bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)


def send_message(text):
    for chat_id in settings.ADMIN_TELEGRAM_CHAT_IDS:
        bot.send_message(chat_id=chat_id, text=text)
