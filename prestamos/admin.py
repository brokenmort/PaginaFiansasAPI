from django.contrib import admin

# Register your models here.
from django.contrib import admin
from prestamos.models import Prestamos

@admin.register(Prestamos)
class PrestamosAdmin(admin.ModelAdmin):
    list_display = ('name', 'reason', 'quantity', 'payment', 'date_created', 'period', 'status', 'answer')
    
