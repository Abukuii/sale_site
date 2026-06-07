#!/bin/bash
# Qurilish Mollari CRM - Setup va ishga tushirish skripti

echo "================================================"
echo "  Qurilish Mollari CRM - O'rnatish"
echo "================================================"

# Virtual environment
echo ""
echo "[1/5] Virtual environment yaratilmoqda..."
python3 -m venv venv
source venv/bin/activate

# Dependencies
echo "[2/5] Django o'rnatilmoqda..."
pip install -r requirements.txt -q

# Migrations
echo "[3/5] Ma'lumotlar bazasi yaratilmoqda..."
python manage.py makemigrations
python manage.py migrate

# Superuser
echo ""
echo "[4/5] Admin foydalanuvchi yaratish"
echo "      (Enter bosib default qiymatlarni qabul qiling yoki o'z ma'lumotlaringizni kiriting)"
echo ""
python manage.py createsuperuser

# Static files
echo ""
echo "[5/5] Static fayllar to'planmoqda..."
python manage.py collectstatic --noinput 2>/dev/null || true

echo ""
echo "================================================"
echo "  O'rnatish tugadi!"
echo "================================================"
echo ""
echo "  Serverni ishga tushirish:"
echo "  source venv/bin/activate"
echo "  python manage.py runserver"
echo ""
echo "  Keyin brauzerda oching:"
echo "  http://127.0.0.1:8000/"
echo ""
echo "  Admin panel:"
echo "  http://127.0.0.1:8000/admin/"
echo "================================================"
