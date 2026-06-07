# qurilish_crm/settings.py ga QO'SHILISHI KERAK BO'LGAN QISMLAR
# ============================================================
# 1. INSTALLED_APPS ga qo'shing:
#
#   'rest_framework',
#   'rest_framework.authtoken',
#
# ============================================================
# 2. settings.py oxiriga qo'shing:

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
}

# ============================================================
# 3. qurilish_crm/urls.py ga qo'shing:
#
#   path('api/', include('crm.api_urls')),
#
# ============================================================
# 4. O'rnatish:
#
#   pip install djangorestframework
#
# ============================================================
# 5. Migration:
#
#   python manage.py migrate   (authtoken jadvali yaratiladi)
#
# ============================================================
# 6. Token olish (birinchi marta):
#
#   python manage.py drf_create_token <username>
#
# ============================================================
