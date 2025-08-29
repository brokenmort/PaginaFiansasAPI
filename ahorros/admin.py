from django.contrib import admin
from .models import Ahorros

# Register your models here.

@admin.register(Ahorros)
class Ahorros(admin.ModelAdmin):
    list_display = ('name', 'reason', 'quantity', 'payment', 'loan', 'date_created', 'date_updated', 'date_final', 'period', 'accrued', 'missing')
    search_fields = ('name', 'reason')
    list_filter = ['period']