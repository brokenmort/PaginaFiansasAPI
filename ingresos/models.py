from django.db import models  # Django ORM base classes and fields
from django.conf import settings  # To reference the custom user model
class IngresosFijos(models.Model):
    # Owner: user that owns this record (FK to users.User). If the user is deleted, cascade.
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ingresos_fijos')
    # Name of the income source (e.g., salary)
    name = models.CharField(max_length=255)
    # Reason or description for context
    reason = models.TextField()
    # Amount of the fixed income
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    # Period label (e.g., 'Mensual', 'Anual')
    period = models.CharField(max_length=100, default='Mensual')
       
    class Meta:
        verbose_name_plural = "Ingresos Fijos"

    def __str__(self):
        # Human-readable representation
        return self.name

    def get_absolute_url(self):
        # Optional: path-like string for UI context
        return f"/IngresosFijos/{self.name}/"


class IngresosExtra(models.Model):
    # Owner: user that owns this record
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ingresos_extra')
    # Name of the income source (e.g., freelance)
    name = models.CharField(max_length=255)
    # Reason or description
    reason = models.TextField()
    # Amount of the extra income
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    # Effective date of the income
    date = models.DateField()
    
    class Meta:
        verbose_name_plural = "Ingresos Extra"

    def __str__(self):
        # Human-readable representation
        return self.name

    def get_absolute_url(self):
        # Optional: path-like string for UI context
        return f"/IngresosExtra/{self.name}/"
