from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from decimal import Decimal, InvalidOperation
from ahorros.models import Ahorros, AhorroMovimiento
from ahorros.api.serializers import AhorrosSerializer, AhorroMovimientoSerializer


@method_decorator(name='list', decorator=swagger_auto_schema(tags=['Ahorros'], operation_summary='Listar ahorros'))
@method_decorator(name='create', decorator=swagger_auto_schema(tags=['Ahorros'], operation_summary='Crear ahorro', request_body=openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['name','reason','quantity','payment','period'],
    properties={
        'name': openapi.Schema(type=openapi.TYPE_STRING, example='Viaje'),
        'reason': openapi.Schema(type=openapi.TYPE_STRING, example='Vacaciones'),
        'quantity': openapi.Schema(type=openapi.TYPE_STRING, example='2000.00'),
        'payment': openapi.Schema(type=openapi.TYPE_STRING, example='200.00'),
        'loan': openapi.Schema(type=openapi.TYPE_BOOLEAN, example=False),
        'period': openapi.Schema(type=openapi.TYPE_STRING, example='Mensual'),
        'accrued': openapi.Schema(type=openapi.TYPE_STRING, example='0.00'),
        'missing': openapi.Schema(type=openapi.TYPE_STRING, example='2000.00')
    }
)))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(tags=['Ahorros'], operation_summary='Detalle de un ahorro'))
@method_decorator(name='update', decorator=swagger_auto_schema(tags=['Ahorros'], operation_summary='Actualizar ahorro'))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(tags=['Ahorros'], operation_summary='Actualizar parcialmente ahorro'))
@method_decorator(name='destroy', decorator=swagger_auto_schema(tags=['Ahorros'], operation_summary='Eliminar ahorro'))
class AhorrosApiViewSet(ModelViewSet):
    # ViewSet for Ahorros
    serializer_class = AhorrosSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name', 'quantity', 'period']

    def get_queryset(self):
        user = getattr(self.request, 'user', None)
        if not user or not user.is_authenticated:
            return Ahorros.objects.none()
        return Ahorros.objects.filter(owner=user).order_by('-id')

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @swagger_auto_schema(methods=['get'], tags=['Ahorros'], operation_summary="Listar movimientos", responses={200: AhorroMovimientoSerializer(many=True)})
    @swagger_auto_schema(methods=['post'], tags=['Ahorros'], operation_summary="Crear movimiento", request_body=AhorroMovimientoSerializer, responses={201: AhorroMovimientoSerializer})
    @action(detail=True, methods=['get', 'post'])
    def movimientos(self, request, pk=None):
        """Lista o crea movimientos asociados a un ahorro."""
        ahorro = self.get_object()
        if request.method.lower() == 'get':
            movimientos = ahorro.movimientos.all()
            ser = AhorroMovimientoSerializer(movimientos, many=True)
            return Response(ser.data)

        # POST crear movimiento gen�rico (pos/neg)
        ser = AhorroMovimientoSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        amount = ser.validated_data['amount']
        # Guardar movimiento
        mov = AhorroMovimiento.objects.create(
            owner=request.user,
            ahorro=ahorro,
            amount=amount,
            date=ser.validated_data.get('date'),
            note=ser.validated_data.get('note', ''),
        )
        # Actualizar acumulado y faltante
        ahorro.accrued = (Decimal(ahorro.accrued) + Decimal(amount))
        ahorro.missing = max(Decimal(0), Decimal(ahorro.quantity) - Decimal(ahorro.accrued))
        ahorro.save()
        return Response(AhorroMovimientoSerializer(mov).data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        method='post',
        tags=['Ahorros'],
        operation_summary='Depositar en ahorro',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['amount'],
            properties={
                'amount': openapi.Schema(type=openapi.TYPE_STRING, example='200.00'),
                'note': openapi.Schema(type=openapi.TYPE_STRING, example='salario'),
            },
        ),
        responses={201: AhorroMovimientoSerializer}
    )
    @action(detail=True, methods=['post'])
    def depositar(self, request, pk=None):
        """Atajo para depositar un monto positivo al ahorro."""
        ahorro = self.get_object()
        try:
            amount = Decimal(str(request.data.get('amount', '0')))
        except (InvalidOperation, TypeError):
            return Response({'detail': 'amount inv�lido'}, status=400)
        if amount <= 0:
            return Response({'detail': 'amount debe ser > 0'}, status=400)
        note = request.data.get('note', '')
        mov = AhorroMovimiento.objects.create(owner=request.user, ahorro=ahorro, amount=amount, note=note)
        ahorro.accrued = Decimal(ahorro.accrued) + amount
        ahorro.missing = max(Decimal(0), Decimal(ahorro.quantity) - Decimal(ahorro.accrued))
        ahorro.save()
        return Response(AhorroMovimientoSerializer(mov).data, status=201)

    @swagger_auto_schema(
        method='post',
        tags=['Ahorros'],
        operation_summary='Retirar del ahorro',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['amount'],
            properties={
                'amount': openapi.Schema(type=openapi.TYPE_STRING, example='50.00'),
                'note': openapi.Schema(type=openapi.TYPE_STRING, example='imprevisto'),
            },
        ),
        responses={201: AhorroMovimientoSerializer}
    )
    @action(detail=True, methods=['post'])
    def retirar(self, request, pk=None):
        """Atajo para retirar un monto (reduce accrued)."""
        ahorro = self.get_object()
        try:
            amount = Decimal(str(request.data.get('amount', '0')))
        except (InvalidOperation, TypeError):
            return Response({'detail': 'amount inv�lido'}, status=400)
        if amount <= 0:
            return Response({'detail': 'amount debe ser > 0'}, status=400)
        if Decimal(ahorro.accrued) - amount < 0:
            return Response({'detail': 'retiro excede el acumulado actual'}, status=400)
        note = request.data.get('note', '')
        mov = AhorroMovimiento.objects.create(owner=request.user, ahorro=ahorro, amount=-amount, note=note)
        ahorro.accrued = Decimal(ahorro.accrued) - amount
        ahorro.missing = max(Decimal(0), Decimal(ahorro.quantity) - Decimal(ahorro.accrued))
        ahorro.save()
        return Response(AhorroMovimientoSerializer(mov).data, status=201)
