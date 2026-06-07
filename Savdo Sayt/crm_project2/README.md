# Qurilish Mollari CRM

Qurilish materiallari do'koni uchun to'liq CRM tizimi.

## Imkoniyatlar

- **Dashboard** — Bugungi savdolar, daromad, haftalik grafik
- **Yangi Savdo** — Mahsulot sotish (naqd, plastik, nasiya)
- **Savdo Tarixi** — Barcha savdolar ro'yxati
- **Mahsulotlar** — Qo'shish, tahrirlash, o'chirish
- **Kam Qolganlar** — Zaxira ogohlantirishlari
- **Qarzdorlar** — Nasiya mijozlar va qarz to'lash
- **Admin Panel** — To'liq boshqaruv `/admin/`
- **Profil** — Foydalanuvchi sozlamalari

## O'rnatish

```bash
# 1. Papkaga kiring
cd qurilish_crm

# 2. Virtual environment yarating
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# yoki
venv\Scripts\activate  # Windows

# 3. Django o'rnating
pip install -r requirements.txt

# 4. Ma'lumotlar bazasini yarating
python manage.py makemigrations
python manage.py migrate

# 5. Admin foydalanuvchi yarating
python manage.py createsuperuser

# 6. Serverni ishga tushiring
python manage.py runserver
```

## Yoki avtomatik o'rnatish (Linux/Mac)

```bash
chmod +x setup.sh
./setup.sh
```

## Kirish

- **Asosiy:** http://127.0.0.1:8000/
- **Login:** http://127.0.0.1:8000/login/
- **Admin:** http://127.0.0.1:8000/admin/

## Texnologiyalar

- **Backend:** Python 3, Django 4.2
- **Database:** SQLite (production'da PostgreSQL tavsiya)
- **Frontend:** HTML5, CSS3, JavaScript (vanilla)
- **Ikonalar:** Font Awesome 6
- **Shrift:** Plus Jakarta Sans
- **Grafiklar:** Chart.js
