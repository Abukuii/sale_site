import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv

from database import get_daily_report, get_monthly_stats, get_qarzdorlar
from config import ADMIN_CHAT_IDS

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()
scheduler = AsyncIOScheduler(timezone="Asia/Tashkent")


# ── KOMANDALAR ────────────────────────────────────────────────
@dp.message(Command("start"))
async def cmd_start(message: Message):
    chat_id = message.chat.id
    await message.answer(
        f"👷 <b>Qurilish Mollari CRM Boti</b>\n\n"
        f"Salom! Bu bot CRM tizimi bilan bog'liq.\n\n"
        f"📋 <b>Mavjud buyruqlar:</b>\n"
        f"/hisobot — Bugungi hisobot\n"
        f"/oylik — Oylik statistika\n"
        f"/qarzdorlar — Qarzdorlar ro'yxati\n"
        f"/chatid — Chat ID ni ko'rish\n\n"
        f"🔔 Har kuni <b>08:00</b> da avtomatik hisobot yuboriladi.",
        parse_mode="HTML"
    )


@dp.message(Command("chatid"))
async def cmd_chatid(message: Message):
    await message.answer(
        f"🆔 Sizning Chat ID: <code>{message.chat.id}</code>\n\n"
        f"Bu ID ni <code>.env</code> faylidagi "
        f"<code>ADMIN_CHAT_IDS</code> ga qo'shing.",
        parse_mode="HTML"
    )


@dp.message(Command("hisobot"))
async def cmd_hisobot(message: Message):
    if not is_admin(message.chat.id):
        await message.answer("❌ Ruxsat yo'q.")
        return
    await message.answer("⏳ Hisobot tayyorlanmoqda...")
    text = await build_daily_report()
    await message.answer(text, parse_mode="HTML")


@dp.message(Command("oylik"))
async def cmd_oylik(message: Message):
    if not is_admin(message.chat.id):
        await message.answer("❌ Ruxsat yo'q.")
        return
    await message.answer("⏳ Oylik statistika tayyorlanmoqda...")
    text = await build_monthly_report()
    await message.answer(text, parse_mode="HTML")


@dp.message(Command("qarzdorlar"))
async def cmd_qarzdorlar(message: Message):
    if not is_admin(message.chat.id):
        await message.answer("❌ Ruxsat yo'q.")
        return
    text = await build_qarzdorlar_report()
    await message.answer(text, parse_mode="HTML")


# ── HISOBOT BUILDER FUNKSIYALAR ───────────────────────────────
async def build_daily_report() -> str:
    data = get_daily_report()
    if not data:
        return "📭 Bugun hech qanday savdo amalga oshirilmagan."

    lines = [
        "📊 <b>Bugungi Savdo Hisoboti</b>",
        f"📅 {data['sana']}\n",
        f"🛒 Jami savdolar: <b>{data['savdolar_soni']} ta</b>",
        f"💵 Naqd: <b>{data['naqd']:,} so'm</b>",
        f"💳 Plastik: <b>{data['plastik']:,} so'm</b>",
        f"📋 Nasiya: <b>{data['nasiya']:,} so'm</b>",
        f"━━━━━━━━━━━━━━━━━",
        f"💰 Jami daromad: <b>{data['jami']:,} so'm</b>",
    ]

    if data.get('top_mahsulotlar'):
        lines.append("\n🏆 <b>Top mahsulotlar:</b>")
        for i, m in enumerate(data['top_mahsulotlar'], 1):
            lines.append(f"  {i}. {m['nomi']} — {m['soni']} ta")

    if data.get('yangi_qarzdorlar'):
        lines.append(f"\n⚠️ Yangi nasiya: <b>{data['yangi_qarzdorlar']} ta</b>")

    return "\n".join(lines)


async def build_monthly_report() -> str:
    data = get_monthly_stats()
    lines = [
        "📈 <b>Oylik Statistika</b>",
        f"📅 {data['oy']}\n",
        f"🛒 Jami savdolar: <b>{data['savdolar_soni']} ta</b>",
        f"💰 Jami daromad: <b>{data['jami_daromad']:,} so'm</b>",
        f"📋 Nasiya miqdori: <b>{data['nasiya_jami']:,} so'm</b>",
        f"👥 Yangi mijozlar: <b>{data['yangi_mijozlar']} ta</b>",
        f"━━━━━━━━━━━━━━━━━",
        f"📦 Eng ko'p sotilgan: <b>{data.get('top_mahsulot', '—')}</b>",
    ]
    return "\n".join(lines)


async def build_qarzdorlar_report() -> str:
    qarzdorlar = get_qarzdorlar()
    if not qarzdorlar:
        return "✅ <b>Qarzdor yo'q!</b> Barcha to'lovlar amalga oshirilgan."

    lines = [
        f"💳 <b>Qarzdorlar Ro'yxati</b>",
        f"Jami: {len(qarzdorlar)} ta mijoz\n"
    ]
    jami_qarz = 0
    for q in qarzdorlar:
        lines.append(
            f"👤 <b>{q['ism']}</b>\n"
            f"   📞 {q['telefon']}\n"
            f"   💸 Qarz: {q['qarz']:,} so'm\n"
        )
        jami_qarz += q['qarz']

    lines.append(f"━━━━━━━━━━━━━━━━━")
    lines.append(f"💰 Umumiy qarz: <b>{jami_qarz:,} so'm</b>")
    return "\n".join(lines)


# ── BILDIRISHNOMA: YANGI NASIYA ───────────────────────────────
async def notify_yangi_nasiya(mijoz_ism: str, telefon: str, summa: int):
    """CRM views.py dan chaqiriladi — yangi nasiya qo'shilganda."""
    text = (
        f"🔔 <b>Yangi Nasiya Qo'shildi!</b>\n\n"
        f"👤 Mijoz: <b>{mijoz_ism}</b>\n"
        f"📞 Tel: {telefon}\n"
        f"💸 Summa: <b>{summa:,} so'm</b>\n\n"
        f"⚠️ To'lov nazorat qiling!"
    )
    for chat_id in ADMIN_CHAT_IDS:
        try:
            await bot.send_message(chat_id, text, parse_mode="HTML")
        except Exception as e:
            logger.error(f"Xabar yuborishda xato {chat_id}: {e}")


# ── SCHEDULER: KUNLIK HISOBOT ─────────────────────────────────
async def send_daily_report_scheduled():
    """Har kuni 08:00 da avtomatik yuboriladi."""
    logger.info("Kunlik hisobot yuborilmoqda...")
    text = await build_daily_report()
    for chat_id in ADMIN_CHAT_IDS:
        try:
            await bot.send_message(chat_id, text, parse_mode="HTML")
            logger.info(f"Hisobot yuborildi: {chat_id}")
        except Exception as e:
            logger.error(f"Xato {chat_id}: {e}")


# ── YORDAMCHI ─────────────────────────────────────────────────
def is_admin(chat_id: int) -> bool:
    return chat_id in ADMIN_CHAT_IDS


# ── ISHGA TUSHIRISH ───────────────────────────────────────────
async def main():
    # Har kuni soat 08:00 da hisobot
    scheduler.add_job(
        send_daily_report_scheduled,
        trigger="cron",
        hour=8,
        minute=0,
        id="daily_report"
    )
    scheduler.start()
    logger.info("Bot ishga tushdi ✅")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
