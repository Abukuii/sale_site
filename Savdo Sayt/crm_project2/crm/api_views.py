# crm/api_views.py
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta

from .models import Mahsulot, Mijoz, Savdo, SavdoItem
from .serializers import (
    MahsulotSerializer, MijozSerializer, SavdoSerializer,
    SavdoCreateSerializer, QarzdorSerializer
)


# ── AUTH ──────────────────────────────────────────────────────
class CustomAuthToken(ObtainAuthToken):
    """POST /api/login/ — token olish."""
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username,
            'is_admin': user.is_superuser,
        })


class LogoutView(APIView):
    """POST /api/logout/ — tokenni o'chirish."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        return Response({'detail': "Muvaffaqiyatli chiqildi."})


# ── MAHSULOTLAR ───────────────────────────────────────────────
class MahsulotViewSet(viewsets.ModelViewSet):
    """
    GET    /api/mahsulotlar/          — ro'yxat
    POST   /api/mahsulotlar/          — qo'shish
    GET    /api/mahsulotlar/{id}/     — bittasi
    PUT    /api/mahsulotlar/{id}/     — yangilash
    DELETE /api/mahsulotlar/{id}/     — o'chirish
    GET    /api/mahsulotlar/kam_qolganlar/ — kam qolganlar
    GET    /api/mahsulotlar/statistika/   — umumiy statistika
    """
    queryset = Mahsulot.objects.all()
    serializer_class = MahsulotSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nomi']
    ordering_fields = ['nomi', 'soni', 'narxi', 'yaratilgan']
    ordering = ['-yaratilgan']

    @action(detail=False, methods=['get'])
    def kam_qolganlar(self, request):
        """20 ta va undan kam qolgan mahsulotlar."""
        chegara = int(request.query_params.get('chegara', 20))
        mahsulotlar = Mahsulot.objects.filter(soni__lte=chegara).order_by('soni')
        serializer = self.get_serializer(mahsulotlar, many=True)
        return Response({
            'count': mahsulotlar.count(),
            'chegara': chegara,
            'results': serializer.data
        })

    @action(detail=False, methods=['get'])
    def statistika(self, request):
        """Mahsulotlar bo'yicha umumiy statistika."""
        qs = Mahsulot.objects.all()
        return Response({
            'jami_turlar': qs.count(),
            'jami_miqdor': qs.aggregate(s=Sum('soni'))['s'] or 0,
            'jami_sotildi': qs.aggregate(s=Sum('sotildi'))['s'] or 0,
            'kam_qolganlar': qs.filter(soni__lte=10).count(),
            'tugaganlar': qs.filter(soni=0).count(),
        })


# ── SAVDOLAR ──────────────────────────────────────────────────
class SavdoViewSet(viewsets.ModelViewSet):
    """
    GET    /api/savdolar/             — ro'yxat (filter: sana, tolov_turi, to_langan)
    POST   /api/savdolar/             — yangi savdo (itemlar bilan)
    GET    /api/savdolar/{id}/        — bittasi
    GET    /api/savdolar/statistika/  — daromad statistikasi
    POST   /api/savdolar/{id}/tolash/ — nasiyani to'langan deb belgilash
    """
    queryset = Savdo.objects.select_related('mijoz').prefetch_related('savdo_itemlar__mahsulot')
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering = ['-yaratilgan']

    def get_serializer_class(self):
        if self.action == 'create':
            return SavdoCreateSerializer
        return SavdoSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        # Filterlar
        sana = self.request.query_params.get('sana')
        tolov = self.request.query_params.get('tolov_turi')
        tolangan = self.request.query_params.get('to_langan')
        if sana:
            qs = qs.filter(sana=sana)
        if tolov:
            qs = qs.filter(tolov_turi=tolov)
        if tolangan is not None:
            qs = qs.filter(to_langan=(tolangan.lower() == 'true'))
        return qs

    @action(detail=True, methods=['post'])
    def tolash(self, request, pk=None):
        """Nasiyani to'langan deb belgilash."""
        savdo = self.get_object()
        if savdo.to_langan:
            return Response({'detail': 'Bu savdo allaqachon to\'langan.'}, status=400)
        savdo.to_langan = True
        savdo.save()
        return Response({'detail': 'To\'lov muvaffaqiyatli amalga oshirildi.', 'id': savdo.pk})

    @action(detail=False, methods=['get'])
    def statistika(self, request):
        """Savdo statistikasi — bugun, oy, yil."""
        bugun = timezone.now().date()
        oy_boshi = bugun.replace(day=1)
        yil_boshi = bugun.replace(month=1, day=1)

        def summa(qs):
            return qs.aggregate(s=Sum('jami_summa'))['s'] or 0

        haftalik = []
        for i in range(6, -1, -1):
            kun = bugun - timedelta(days=i)
            haftalik.append({
                'sana': kun.isoformat(),
                'summa': float(summa(Savdo.objects.filter(sana=kun)))
            })

        return Response({
            'bugun': {
                'soni': Savdo.objects.filter(sana=bugun).count(),
                'summa': float(summa(Savdo.objects.filter(sana=bugun))),
            },
            'oy': {
                'soni': Savdo.objects.filter(sana__gte=oy_boshi).count(),
                'summa': float(summa(Savdo.objects.filter(sana__gte=oy_boshi))),
            },
            'yil': {
                'soni': Savdo.objects.filter(sana__gte=yil_boshi).count(),
                'summa': float(summa(Savdo.objects.filter(sana__gte=yil_boshi))),
            },
            'haftalik': haftalik,
        })


# ── MIJOZLAR & QARZDORLAR ─────────────────────────────────────
class MijozViewSet(viewsets.ModelViewSet):
    """
    GET    /api/mijozlar/             — ro'yxat
    POST   /api/mijozlar/             — qo'shish
    GET    /api/mijozlar/{id}/        — bittasi
    PUT    /api/mijozlar/{id}/        — yangilash
    DELETE /api/mijozlar/{id}/        — o'chirish
    """
    queryset = Mijoz.objects.all()
    serializer_class = MijozSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['ism_familiya', 'telefon']

    @action(detail=False, methods=['get'])
    def qarzdorlar(self, request):
        """Faqat qarzi bor mijozlar."""
        mijozlar = Mijoz.objects.filter(
            savdolar__to_langan=False
        ).distinct()
        serializer = QarzdorSerializer(mijozlar, many=True)
        jami = sum(m.jami_qarz for m in mijozlar)
        return Response({
            'count': mijozlar.count(),
            'umumiy_qarz': float(jami),
            'results': serializer.data
        })
