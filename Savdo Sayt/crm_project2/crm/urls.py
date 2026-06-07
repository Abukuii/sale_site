from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('savdo/', views.savdo, name='savdo'),
    path('mahsulotlar/', views.barcha_mahsulotlar, name='barcha_mahsulotlar'),
    path('kamayganlar/', views.kamayganlar, name='kamayganlar'),
    path('qarzdorlar/', views.qarzdorlar, name='qarzdorlar'),
    path('profil/', views.profil, name='profil'),
    path('tarix/', views.savdo_tarixi, name='savdo_tarixi'),
    path('kirimlar/', views.kirim_tarixi, name='kirim_tarixi'),
]
