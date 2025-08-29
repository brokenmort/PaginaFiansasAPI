from django.db import models
from django.conf import settings
from django.utils import timezone

# Create your models here.
class Ahorros(models.Model):
    # Usuario propietario del registro
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ahorros')
    name = models.CharField(max_length=255)
    reason = models.TextField()
    quantity = models.DecimalField(max_digits=10, decimal_places=2)  # Agrega max_digits
    payment = models.DecimalField(max_digits=10, decimal_places=2)  # Agrega max_digits
    loan = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    date_final = models.DateField(null=True, blank=True)  # Fecha final opcional
    period = models.CharField(max_length=100, default='Mensual')  # Por ejemplo: 'Mensual', 'Anual'
    accrued = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Acumulado
    missing = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Faltante


    class Meta:
        verbose_name_plural = "Ahorros"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f"/Ahorros/{self.name}/"


class AhorroMovimiento(models.Model):
    # Usuario propietario del movimiento (normalmente el mismo del ahorro)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ahorro_movimientos')
    # Ahorro al que pertenece este movimiento
    ahorro = models.ForeignKey(Ahorros, on_delete=models.CASCADE, related_name='movimientos')
    # Monto del movimiento: positivo (depósito) o negativo (retiro)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    # Fecha efectiva del movimiento
    # Fecha (solo fecha, sin hora)
    date = models.DateField(default=timezone.localdate)
    # Nota opcional
    note = models.CharField(max_length=255, blank=True, default='')
    # Marca de tiempo de creación
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-id']
