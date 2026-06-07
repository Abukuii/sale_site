from django.db import models
from django.utils import timezone


class Mahsulot(models.Model):
    nomi = models.CharField(max_length=200, verbose_name="Mahsulot nomi")
    qoldi = models.IntegerField(default=0, verbose_name="Qoldi (joriy)")
    narxi = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="Narxi (so'm)")
    yaratilgan = models.DateTimeField(auto_now_add=True)
    yangilangan = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Mahsulot"
        verbose_name_plural = "Mahsulotlar"
        ordering = ['-yaratilgan']

    def __str__(self):
        return self.nomi

    @property
    def jami_kirim(self):
        return sum(k.soni for k in self.kirimlar.all())

    @property
    def jami_sotildi(self):
        from django.db.models import Sum
        result = SavdoItem.objects.filter(mahsulot=self).aggregate(s=Sum('soni'))['s']
        return result or 0

    @property
    def kam_qolgan(self):
        return self.qoldi <= 10


class Kirim(models.Model):
    mahsulot = models.ForeignKey(
        Mahsulot, on_delete=models.CASCADE,
        related_name='kirimlar', verbose_name="Mahsulot"
    )
    soni = models.IntegerField(verbose_name="Kirim soni")
    narxi = models.DecimalField(max_digits=12, decimal_places=0, null=True, blank=True, verbose_name="Kirim narxi")
    izoh = models.CharField(max_length=300, blank=True, verbose_name="Izoh")
    sana = models.DateField(default=timezone.now, verbose_name="Sana")
    yaratilgan = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Kirim"
        verbose_name_plural = "Kirimlar"
        ordering = ['-yaratilgan']

    def __str__(self):
        return f"{self.mahsulot.nomi} — +{self.soni} ta ({self.sana})"

    def save(self, *args, **kwargs):
        if not self.pk:
            super().save(*args, **kwargs)
            self.mahsulot.qoldi += self.soni
            self.mahsulot.save()
        else:
            super().save(*args, **kwargs)


class Mijoz(models.Model):
    ism_familiya = models.CharField(max_length=200, verbose_name="Ism Familiya")
    telefon = models.CharField(max_length=20, verbose_name="Telefon raqami")
    manzil = models.CharField(max_length=300, blank=True, verbose_name="Manzil")
    yaratilgan = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Mijoz"
        verbose_name_plural = "Mijozlar"
        ordering = ['-yaratilgan']

    def __str__(self):
        return f"{self.ism_familiya} - {self.telefon}"

    @property
    def jami_qarz(self):
        return sum(s.jami_summa for s in self.savdolar.filter(to_langan=False))


class Savdo(models.Model):
    TOLOV_TURI = [
        ('naqd', 'Naqd pul'),
        ('nasiya', 'Nasiya'),
        ('plastik', 'Plastik karta'),
    ]

    mijoz = models.ForeignKey(Mijoz, on_delete=models.CASCADE, related_name='savdolar', null=True, blank=True, verbose_name="Mijoz")
    sana = models.DateField(default=timezone.now, verbose_name="Sana")
    tolov_turi = models.CharField(max_length=10, choices=TOLOV_TURI, default='naqd', verbose_name="To'lov turi")
    jami_summa = models.DecimalField(max_digits=14, decimal_places=0, default=0, verbose_name="Jami summa")
    to_langan = models.BooleanField(default=True, verbose_name="To'langan")
    izoh = models.TextField(blank=True, verbose_name="Izoh")
    yaratilgan = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Savdo"
        verbose_name_plural = "Savdolar"
        ordering = ['-yaratilgan']

    def __str__(self):
        return f"Savdo #{self.pk} - {self.sana}"

    def save(self, *args, **kwargs):
        if self.pk:
            self.jami_summa = sum(item.jami for item in self.savdo_itemlar.all())
        super().save(*args, **kwargs)


class SavdoItem(models.Model):
    savdo = models.ForeignKey(Savdo, on_delete=models.CASCADE, related_name='savdo_itemlar')
    mahsulot = models.ForeignKey(Mahsulot, on_delete=models.CASCADE, verbose_name="Mahsulot")
    soni = models.IntegerField(default=1, verbose_name="Soni")
    narxi = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="Narxi")

    class Meta:
        verbose_name = "Savdo element"
        verbose_name_plural = "Savdo elementlar"

    def __str__(self):
        return f"{self.mahsulot.nomi} x {self.soni}"

    @property
    def jami(self):
        return self.narxi * self.soni
