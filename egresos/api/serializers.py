from rest_framework import serializers
from egresos.models import EgresosFijos, EgresosExtra

class EgresosFijosSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.email')
    class Meta:
        model = EgresosFijos
        fields = '__all__'  # Serializa todos los campos del modelo

class EgresosExtraSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.email')
    class Meta:
        model = EgresosExtra
        fields = '__all__'  # Serializa todos los campos del modelo

