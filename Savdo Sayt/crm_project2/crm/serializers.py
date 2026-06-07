# crm/serializers.py
from rest_framework import serializers
from .models import Mahsulot, Mijoz, Savdo, SavdoItem


class MahsulotSerializer(serializers.ModelSerializer):
    qoldi = serializers.ReadOnlyField()
    kam_qolgan = serializers.ReadOnlyField()

    class Meta:
        model = Mahsulot
        fields = ['id', 'nomi', 'soni', 'narxi', 'sotildi', 'qoldi', 'kam_qolgan', 'yaratilgan']
        read_only_fields = ['sotildi', 'yaratilgan']


class SavdoItemSerializer(serializers.ModelSerializer):
    mahsulot_nomi = serializers.CharField(source='mahsulot.nomi', read_only=True)
    jami = serializers.ReadOnlyField()

    class Meta:
        model = SavdoItem
        fields = ['id', 'mahsulot', 'mahsulot_nomi', 'soni', 'narxi', 'jami']


class SavdoSerializer(serializers.ModelSerializer):
    savdo_itemlar = SavdoItemSerializer(many=True, read_only=True)
    mijoz_ism = serializers.CharField(source='mijoz.ism_familiya', read_only=True)

    class Meta:
        model = Savdo
        fields = ['id', 'mijoz', 'mijoz_ism', 'sana', 'tolov_turi',
                  'jami_summa', 'to_langan', 'izoh', 'savdo_itemlar', 'yaratilgan']
        read_only_fields = ['jami_summa', 'yaratilgan']


class SavdoCreateSerializer(serializers.ModelSerializer):
    """Yangi savdo yaratish uchun — itemlar bilan birga."""
    itemlar = serializers.ListField(
        child=serializers.DictField(), write_only=True
    )

    class Meta:
        model = Savdo
        fields = ['mijoz', 'sana', 'tolov_turi', 'izoh', 'itemlar']

    def create(self, validated_data):
        itemlar_data = validated_data.pop('itemlar', [])
        savdo = Savdo.objects.create(**validated_data,
                                     to_langan=(validated_data.get('tolov_turi') != 'nasiya'),
                                     jami_summa=0)
        jami = 0
        for item in itemlar_data:
            mahsulot = Mahsulot.objects.get(pk=item['mahsulot_id'])
            son = int(item['soni'])
            SavdoItem.objects.create(
                savdo=savdo, mahsulot=mahsulot,
                soni=son, narxi=mahsulot.narxi
            )
            mahsulot.sotildi += son
            mahsulot.save()
            jami += mahsulot.narxi * son
        savdo.jami_summa = jami
        savdo.save()
        return savdo


class MijozSerializer(serializers.ModelSerializer):
    jami_qarz = serializers.ReadOnlyField()
    savdolar_soni = serializers.SerializerMethodField()

    class Meta:
        model = Mijoz
        fields = ['id', 'ism_familiya', 'telefon', 'manzil',
                  'jami_qarz', 'savdolar_soni', 'yaratilgan']
        read_only_fields = ['yaratilgan']

    def get_savdolar_soni(self, obj):
        return obj.savdolar.count()


class QarzdorSerializer(serializers.ModelSerializer):
    """Faqat nasiya qarzlari bor mijozlar."""
    jami_qarz = serializers.ReadOnlyField()
    nasiya_savdolar = serializers.SerializerMethodField()

    class Meta:
        model = Mijoz
        fields = ['id', 'ism_familiya', 'telefon', 'manzil', 'jami_qarz', 'nasiya_savdolar']

    def get_nasiya_savdolar(self, obj):
        savdolar = obj.savdolar.filter(to_langan=False)
        return SavdoSerializer(savdolar, many=True).data
