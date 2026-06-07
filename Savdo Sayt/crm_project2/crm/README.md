# Qurilish Mollari CRM — REST API

## O'rnatish (4 qadam)

### 1. DRF o'rnating
```bash
pip install djangorestframework
```

### 2. settings.py ga qo'shing
```python
INSTALLED_APPS = [
    ...
    'rest_framework',
    'rest_framework.authtoken',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}
```

### 3. urls.py ga qo'shing
```python
path('api/', include('crm.api_urls')),
```

### 4. Fayllarni ko'chiring
```
serializers.py   → crm/serializers.py
api_views.py     → crm/api_views.py
api_urls.py      → crm/api_urls.py
```

### 5. Migrate va token yarating
```bash
python manage.py migrate
python manage.py drf_create_token admin
```

---

## Barcha Endpoints

| Method | URL | Tavsif |
|--------|-----|--------|
| POST | `/api/login/` | Token olish |
| POST | `/api/logout/` | Chiqish |
| GET/POST | `/api/mahsulotlar/` | Ro'yxat / qo'shish |
| GET/PUT/DELETE | `/api/mahsulotlar/{id}/` | Ko'rish / yangilash / o'chirish |
| GET | `/api/mahsulotlar/kam_qolganlar/` | Kam qolganlar |
| GET | `/api/mahsulotlar/statistika/` | Statistika |
| GET/POST | `/api/savdolar/` | Ro'yxat / yangi savdo |
| GET | `/api/savdolar/{id}/` | Bitta savdo |
| POST | `/api/savdolar/{id}/tolash/` | Nasiyani to'lash |
| GET | `/api/savdolar/statistika/` | Daromad statistikasi |
| GET/POST | `/api/mijozlar/` | Ro'yxat / qo'shish |
| GET/PUT/DELETE | `/api/mijozlar/{id}/` | Ko'rish / yangilash / o'chirish |
| GET | `/api/mijozlar/qarzdorlar/` | Qarzdorlar |

## Token bilan so'rov
```bash
curl -H "Authorization: Token <TOKEN>" http://127.0.0.1:8000/api/mahsulotlar/
```

## Postman
`CRM_API.postman_collection.json` faylini Postman ga import qiling.
Login qilganda token avtomatik saqlanadi.
