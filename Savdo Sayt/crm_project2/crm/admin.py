from django.contrib import admin
from django.utils.html import format_html
from .models import Mahsulot, Kirim, Mijoz, Savdo, SavdoItem


class SavdoItemInline(admin.TabularInline):
    model = SavdoItem
    extra = 0
    readonly_fields = ['jami_display']

    def jami_display(self, obj):
        return f"{obj.jami:,.0f} so'm"
    jami_display.short_description = "Jami"


@admin.register(Mahsulot)
class MahsulotAdmin(admin.ModelAdmin):
    list_display = ['nomi', 'qoldi', 'narxi_display', 'holat']
    list_filter = ['yaratilgan']
    search_fields = ['nomi']
    ordering = ['nomi']

    def narxi_display(self, obj):
        return f"{obj.narxi:,.0f} so'm"
    narxi_display.short_description = "Narxi"

    def holat(self, obj):
        if obj.qoldi <= 0:
            return format_html('<span style="color:red;font-weight:bold">Tugagan</span>')
        elif obj.qoldi <= 10:
            return format_html('<span style="color:orange;font-weight:bold">Kam qoldi</span>')
        return format_html('<span style="color:green">Yetarli</span>')
    holat.short_description = "Holat"


@admin.register(Kirim)
class KirimAdmin(admin.ModelAdmin):
    list_display = ['mahsulot', 'soni', 'narxi', 'izoh', 'sana', 'yaratilgan']
    list_filter = ['sana', 'mahsulot']
    ordering = ['-yaratilgan']


@admin.register(Mijoz)
class MijozAdmin(admin.ModelAdmin):
    list_display = ['ism_familiya', 'telefon', 'manzil', 'qarz_display', 'yaratilgan']
    search_fields = ['ism_familiya', 'telefon']
    ordering = ['-yaratilgan']

    def qarz_display(self, obj):
        qarz = float(obj.jami_qarz)
        if qarz > 0:
            return format_html(
                '<span style="color:red;font-weight:bold">{} som</span>',
                f"{qarz:,.0f}"
            )
        return format_html('<span style="color:green">Tolangan</span>')
    qarz_display.short_description = "Qarz"


@admin.register(Savdo)
class SavdoAdmin(admin.ModelAdmin):
    list_display = ['pk', 'mijoz', 'sana', 'tolov_turi', 'jami_summa_display', 'to_langan_display']
    list_filter = ['tolov_turi', 'to_langan', 'sana']
    search_fields = ['mijoz__ism_familiya']
    ordering = ['-yaratilgan']
    inlines = [SavdoItemInline]
    date_hierarchy = 'sana'

    def jami_summa_display(self, obj):
        return f"{obj.jami_summa:,.0f} so'm"
    jami_summa_display.short_description = "Jami summa"

    def to_langan_display(self, obj):
        if obj.to_langan:
            return format_html('<span style="color:green;font-weight:bold">Tolangan</span>')
        return format_html('<span style="color:red;font-weight:bold">Nasiya</span>')
    to_langan_display.short_description = "Holat"


admin.site.site_header = "Qurilish Mollari CRM"
admin.site.site_title = "Qurilish CRM Admin"
admin.site.index_title = "Boshqaruv paneli"