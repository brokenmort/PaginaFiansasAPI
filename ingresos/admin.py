from django.contrib import admin
from .models import IngresosFijos, IngresosExtra

# Register your models here.

@admin.register(IngresosFijos)
class IngresosFijosAdmin(admin.ModelAdmin):
    list_display = ('name', 'reason', 'quantity', 'period')
    search_fields = ('name', 'reason')
    list_filter = ('period',)

@admin.register(IngresosExtra)
class IngresosExtraAdmin(admin.ModelAdmin):
    list_display = ('name', 'reason', 'quantity', 'date')
    search_fields = ('name', 'reason')
    list_filter = ('date',)


