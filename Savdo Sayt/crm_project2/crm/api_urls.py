# crm/api_urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    CustomAuthToken, LogoutView,
    MahsulotViewSet, SavdoViewSet, MijozViewSet
)

router = DefaultRouter()
router.register('mahsulotlar', MahsulotViewSet, basename='mahsulot')
router.register('savdolar', SavdoViewSet, basename='savdo')
router.register('mijozlar', MijozViewSet, basename='mijoz')

urlpatterns = [
    path('login/', CustomAuthToken.as_view(), name='api_login'),
    path('logout/', LogoutView.as_view(), name='api_logout'),
    path('', include(router.urls)),
]
