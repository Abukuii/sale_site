from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
import json

from .models import Mahsulot, Kirim, Mijoz, Savdo, SavdoItem


@login_required
def dashboard(request):
    bugun = timezone.now().date()
    oy_boshi = bugun.replace(day=1)

    jami_mahsulotlar = Mahsulot.objects.count()
    jami_savdolar = Savdo.objects.filter(sana=bugun).count()
    bugungi_daromad = Savdo.objects.filter(sana=bugun).aggregate(s=Sum('jami_summa'))['s'] or 0
    oylik_daromad = Savdo.objects.filter(sana__gte=oy_boshi).aggregate(s=Sum('jami_summa'))['s'] or 0
    jami_qarzdorlar = Mijoz.objects.filter(savdolar__to_langan=False).distinct().count()
    kam_qolganlar = Mahsulot.objects.filter(qoldi__lte=10).count()

    haftalik_data = []
    for i in range(6, -1, -1):
        kun = bugun - timedelta(days=i)
        summa = Savdo.objects.filter(sana=kun).aggregate(s=Sum('jami_summa'))['s'] or 0
        haftalik_data.append({'kun': kun.strftime('%d/%m'), 'summa': float(summa)})

    oxirgi_savdolar = Savdo.objects.select_related('mijoz').order_by('-yaratilgan')[:5]

    context = {
        'jami_mahsulotlar': jami_mahsulotlar,
        'jami_savdolar': jami_savdolar,
        'bugungi_daromad': bugungi_daromad,
        'oylik_daromad': oylik_daromad,
        'jami_qarzdorlar': jami_qarzdorlar,
        'kam_qolganlar': kam_qolganlar,
        'haftalik_data': json.dumps(haftalik_data),
        'oxirgi_savdolar': oxirgi_savdolar,
    }
    return render(request, 'crm/dashboard.html', context)


@login_required
def savdo(request):
    mahsulotlar = Mahsulot.objects.filter(qoldi__gt=0)
    mijozlar = Mijoz.objects.all()

    if request.method == 'POST':
        tolov_turi = request.POST.get('tolov_turi', 'naqd')
        mijoz_id = request.POST.get('mijoz_id')
        mijoz_ism = request.POST.get('mijoz_ism', '')
        mijoz_tel = request.POST.get('mijoz_tel', '')

        mijoz = None
        if tolov_turi == 'nasiya':
            if mijoz_id:
                mijoz = get_object_or_404(Mijoz, pk=mijoz_id)
            elif mijoz_ism and mijoz_tel:
                mijoz = Mijoz.objects.create(ism_familiya=mijoz_ism, telefon=mijoz_tel)

        mahsulot_ids = request.POST.getlist('mahsulot_id')
        sonlar = request.POST.getlist('son')
        jami = 0
        itemlar = []

        for mid, son in zip(mahsulot_ids, sonlar):
            if mid and son:
                try:
                    mahsulot = Mahsulot.objects.get(pk=mid)
                    son_int = int(son)
                    if son_int > 0 and mahsulot.qoldi >= son_int:
                        itemlar.append((mahsulot, son_int))
                        jami += mahsulot.narxi * son_int
                except (Mahsulot.DoesNotExist, ValueError):
                    pass

        savdo_obj = Savdo.objects.create(
            mijoz=mijoz,
            tolov_turi=tolov_turi,
            to_langan=(tolov_turi != 'nasiya'),
            jami_summa=jami
        )

        for mahsulot, son_int in itemlar:
            SavdoItem.objects.create(
                savdo=savdo_obj, mahsulot=mahsulot,
                soni=son_int, narxi=mahsulot.narxi
            )
            # Sotilganda qoldiqdan ayriladi
            mahsulot.qoldi -= son_int
            mahsulot.save()

        messages.success(request, f"Savdo #{savdo_obj.pk} muvaffaqiyatli amalga oshirildi!")
        return redirect('savdo')

    context = {'mahsulotlar': mahsulotlar, 'mijozlar': mijozlar}
    return render(request, 'crm/savdo.html', context)


@login_required
def barcha_mahsulotlar(request):
    mahsulotlar = Mahsulot.objects.all()
    search = request.GET.get('q', '')
    if search:
        mahsulotlar = mahsulotlar.filter(nomi__icontains=search)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'qoshish':
            nomi = request.POST.get('nomi')
            qoldi = request.POST.get('qoldi', 0)
            narxi = request.POST.get('narxi', 0)
            if nomi:
                Mahsulot.objects.create(nomi=nomi, qoldi=qoldi, narxi=narxi)
                messages.success(request, f"'{nomi}' mahsuloti qo'shildi!")
        elif action == 'tahrirlash':
            mid = request.POST.get('mahsulot_id')
            mahsulot = get_object_or_404(Mahsulot, pk=mid)
            mahsulot.nomi = request.POST.get('nomi', mahsulot.nomi)
            mahsulot.narxi = request.POST.get('narxi', mahsulot.narxi)
            mahsulot.save()
            messages.success(request, "Mahsulot yangilandi!")
        elif action == 'ochirish':
            mid = request.POST.get('mahsulot_id')
            mahsulot = get_object_or_404(Mahsulot, pk=mid)
            mahsulot.delete()
            messages.success(request, "Mahsulot o'chirildi!")
        elif action == 'kirim':
            # Yangi kirim — qoldiqqa qo'shiladi
            mid = request.POST.get('mahsulot_id')
            mahsulot = get_object_or_404(Mahsulot, pk=mid)
            kirim_soni = int(request.POST.get('kirim_soni', 0))
            kirim_narxi = request.POST.get('kirim_narxi') or None
            izoh = request.POST.get('izoh', '')
            if kirim_soni > 0:
                Kirim.objects.create(
                    mahsulot=mahsulot,
                    soni=kirim_soni,
                    narxi=kirim_narxi,
                    izoh=izoh
                )
                messages.success(request, f"'{mahsulot.nomi}' ga +{kirim_soni} ta kirim qo'shildi!")
            else:
                messages.error(request, "Kirim soni 0 dan katta bo'lishi kerak!")
        return redirect('barcha_mahsulotlar')

    context = {'mahsulotlar': mahsulotlar, 'search': search}
    return render(request, 'crm/barcha.html', context)


@login_required
def kirim_tarixi(request):
    kirimlar = Kirim.objects.select_related('mahsulot').order_by('-yaratilgan')
    context = {'kirimlar': kirimlar}
    return render(request, 'crm/kirim_tarixi.html', context)


@login_required
def kamayganlar(request):
    mahsulotlar = Mahsulot.objects.filter(qoldi__lte=20).order_by('qoldi')
    context = {'mahsulotlar': mahsulotlar}
    return render(request, 'crm/kamayganlar.html', context)


@login_required
def qarzdorlar(request):
    mijozlar = Mijoz.objects.filter(savdolar__to_langan=False).distinct()

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'tolash':
            savdo_id = request.POST.get('savdo_id')
            savdo_obj = get_object_or_404(Savdo, pk=savdo_id)
            savdo_obj.to_langan = True
            savdo_obj.save()
            messages.success(request, "Qarz to'landi!")
        elif action == 'ochirish':
            mijoz_id = request.POST.get('mijoz_id')
            mijoz = get_object_or_404(Mijoz, pk=mijoz_id)
            mijoz.delete()
            messages.success(request, "Mijoz o'chirildi!")
        return redirect('qarzdorlar')

    context = {'mijozlar': mijozlar}
    return render(request, 'crm/qarzdorlar.html', context)


@login_required
def profil(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()
        messages.success(request, "Profil yangilandi!")
        return redirect('profil')

    context = {'user': request.user}
    return render(request, 'crm/profil.html', context)


@login_required
def savdo_tarixi(request):
    savdolar = Savdo.objects.select_related('mijoz').prefetch_related('savdo_itemlar__mahsulot').order_by('-yaratilgan')
    context = {'savdolar': savdolar}
    return render(request, 'crm/tarix.html', context)
