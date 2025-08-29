from rest_framework import serializers
from ahorros.models import Ahorros, AhorroMovimiento

class AhorrosSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.email')
    class Meta:
        model = Ahorros
        fields = '__all__'  # Serializa todos los campos del modelo


class AhorroMovimientoSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.email')
    ahorro = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = AhorroMovimiento
        fields = ['id', 'owner', 'ahorro', 'amount', 'date', 'note', 'created_at']
