from django.db import models
from django.conf import settings


class EgresosFijos(models.Model):
    # Usuario propietario del registro
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='egresos_fijos')
    name = models.CharField(max_length=255)
    reason = models.TextField()
    quantity = models.DecimalField(max_digits=10, decimal_places=2)  # Agrega max_digits
    period = models.CharField(max_length=100, default='Mensual')  # Por ejemplo: 'Mensual', 'Anual'
       
    class Meta:
        verbose_name_plural = "Egresos Fijos"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f"/EgresosFijos/{self.name}/"


class EgresosExtra(models.Model):
    # Usuario propietario del registro
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='egresos_extra')
    name = models.CharField(max_length=255)
    reason = models.TextField()
    quantity = models.DecimalField(max_digits=10, decimal_places=2)  # Agrega max_digits
    date = models.DateField()
    
    class Meta:
        verbose_name_plural = "Egresos Extra"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f"/EgresosExtra/{self.name}/"
