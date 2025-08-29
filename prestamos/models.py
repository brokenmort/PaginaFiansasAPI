from django.db import models
from django.conf import settings

# Create your models here.
class Prestamos(models.Model):
    # Usuario propietario del registro
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='prestamos')
    name = models.CharField(max_length=255)
    reason = models.TextField()
    quantity = models.DecimalField(max_digits=10, decimal_places=2)  # Agrega max_digits
    payment = models.DecimalField(max_digits=10, decimal_places=2)  # Agrega max_digits
    date_created = models.DateTimeField(auto_now_add=True)
    period = models.CharField(max_length=100, default='Mensual')  # Por ejemplo: 'Mensual', 'Anual'
    status = models.CharField(max_length=50, default='Pendiente')  # Por ejemplo: 'Pendiente', 'Aprobado', 'Rechazado'
    answer = models.CharField(max_length=50, default='Favorable')  # Por ejemplo: 'Pendiente', 'Aprobado', 'Rechazado'
 
    class Meta:
        verbose_name_plural = "Prestamos"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f"/Prestamos/{self.name}/"
