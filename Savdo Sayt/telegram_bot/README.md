# Qurilish Mollari CRM — Telegram Bot

## Imkoniyatlar
- ⏰ Har kuni **08:00** da avtomatik hisobot
- 🔔 Yangi nasiya qo'shilganda darhol xabar
- 📊 `/hisobot` — bugungi savdo hisoboti
- 📈 `/oylik` — oylik statistika
- 💳 `/qarzdorlar` — qarzdorlar ro'yxati

## O'rnatish

### 1. Bot Token olish
1. Telegramda **@BotFather** ga yozing
2. `/newbot` buyrug'ini yuboring
3. Bot nomini kiriting → Token oling

### 2. Chat ID olish
1. Botingizga `/start` yuboring
2. `/chatid` yuboring → ID ni ko'chiring

### 3. .env sozlash
```bash
cp .env.example .env
# .env faylini oching va to'ldiring:
# BOT_TOKEN=...
# ADMIN_CHAT_IDS=...
# DB_PATH=../crm_project/db.sqlite3
```

### 4. O'rnatish va ishga tushirish
```bash
cd telegram_bot
pip install -r requirements.txt
python bot.py
```

## CRM bilan integratsiya (yangi nasiya bildirishnomasi)

`crm/apps.py` faylini `apps_yangilangan.py` bilan almashtiring:
```bash
cp apps_yangilangan.py ../crm_project/crm/apps.py
```

## Papka tuzilishi
```
telegram_bot/
├── bot.py              ← Asosiy bot fayli
├── database.py         ← CRM SQLite so'rovlari
├── config.py           ← Sozlamalar
├── signals_for_crm.py  ← Django signal (bildirishnoma)
├── .env.example        ← .env namunasi
└── requirements.txt
```
