# crm/apps.py — YANGILANGAN versiya (signallar bilan)
from django.apps import AppConfig


class CrmConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'crm'
    verbose_name = 'CRM Tizimi'

    def ready(self):
        """Ilova tayyor bo'lganda signallarni ulaydi."""
        try:
            from telegram_bot.signals_for_crm import connect_signals
            connect_signals()
        except ImportError:
            # telegram_bot o'rnatilmagan bo'lsa, o'tkazib yuboradi
            pass
