from django.contrib import admin
from .models import EgresosFijos, EgresosExtra

# Register your models here.

@admin.register(EgresosFijos)
class IngresosFijosAdmin(admin.ModelAdmin):
    list_display = ('name', 'reason', 'quantity', 'period')
    search_fields = ('name', 'reason')
    list_filter = ('period',)

@admin.register(EgresosExtra)
class IngresosExtraAdmin(admin.ModelAdmin):
    list_display = ('name', 'reason', 'quantity', 'date')
    search_fields = ('name', 'reason')
    list_filter = ('date',)


