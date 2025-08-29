from rest_framework import serializers
from prestamos.models import Prestamos

class PrestamosSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.email')
    # Serializer for the Prestamos model
    class Meta:
        model = Prestamos
        fields = ['id', 'owner', 'name', 'reason', 'quantity', 'payment', 'date_created', 'period', 'status', 'answer']
