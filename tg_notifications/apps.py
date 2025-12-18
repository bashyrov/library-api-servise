from django.apps import AppConfig


class TgNotificationsConfig(AppConfig):
    name = 'tg_notifications'

    def ready(self):
        import tg_notifications.signals
