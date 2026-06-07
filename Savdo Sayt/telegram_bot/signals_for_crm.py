"""
crm/signals.py — bu faylni crm/ papkasiga qo'ying.

Django signal: yangi nasiya savdo saqlananda Telegram botga xabar yuboradi.
"""
import asyncio
import os
import logging
import django
from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


def _send_nasiya_notify(mijoz_ism: str, telefon: str, summa: int):
    """Synchronous wrapper — Django signal dan asinxron bot chaqirish."""
    try:
        import sys
        # telegram_bot papkasi PATH da bo'lishi kerak
        bot_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'telegram_bot')
        sys.path.insert(0, os.path.abspath(bot_dir))

        from aiogram import Bot
        from dotenv import load_dotenv
        load_dotenv(os.path.join(bot_dir, '.env'))

        bot_token = os.getenv("BOT_TOKEN", "")
        admin_ids_raw = os.getenv("ADMIN_CHAT_IDS", "")
        admin_ids = [int(x.strip()) for x in admin_ids_raw.split(",") if x.strip().isdigit()]

        if not bot_token or not admin_ids:
            logger.warning("BOT_TOKEN yoki ADMIN_CHAT_IDS sozlanmagan")
            return

        text = (
            f"🔔 <b>Yangi Nasiya Qo'shildi!</b>\n\n"
            f"👤 Mijoz: <b>{mijoz_ism}</b>\n"
            f"📞 Tel: {telefon}\n"
            f"💸 Summa: <b>{summa:,} so'm</b>\n\n"
            f"⚠️ To'lovni nazorat qiling!"
        )

        async def _send():
            bot = Bot(token=bot_token)
            for chat_id in admin_ids:
                try:
                    await bot.send_message(chat_id, text, parse_mode="HTML")
                except Exception as e:
                    logger.error(f"Xabar yuborishda xato: {e}")
            await bot.session.close()

        asyncio.run(_send())

    except Exception as e:
        logger.error(f"Telegram bildirishnoma xatosi: {e}")


# Signal ulash
def connect_signals():
    """crm/apps.py ready() metodidan chaqiring."""
    from crm.models import Savdo

    @receiver(post_save, sender=Savdo)
    def savdo_post_save(sender, instance, created, **kwargs):
        if created and instance.tolov_turi == 'nasiya' and instance.mijoz:
            mijoz = instance.mijoz
            _send_nasiya_notify(
                mijoz_ism=mijoz.ism_familiya,
                telefon=mijoz.telefon,
                summa=int(instance.jami_summa)
            )
