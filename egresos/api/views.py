from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from egresos.models import EgresosFijos, EgresosExtra
from egresos.api.serializers import EgresosFijosSerializer, EgresosExtraSerializer

@method_decorator(name='list', decorator=swagger_auto_schema(tags=['Egresos'], operation_summary='Listar egresos fijos', responses={200: EgresosFijosSerializer(many=True)}))
@method_decorator(name='create', decorator=swagger_auto_schema(tags=['Egresos'], operation_summary='Crear egreso fijo', request_body=openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['name','reason','quantity'],
    properties={
        'name': openapi.Schema(type=openapi.TYPE_STRING, example='Renta'),
        'reason': openapi.Schema(type=openapi.TYPE_STRING, example='Alquiler'),
        'quantity': openapi.Schema(type=openapi.TYPE_STRING, example='500.00'),
        'period': openapi.Schema(type=openapi.TYPE_STRING, example='Mensual')
    }
)))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(tags=['Egresos'], operation_summary='Detalle de egreso fijo'))
@method_decorator(name='update', decorator=swagger_auto_schema(tags=['Egresos'], operation_summary='Actualizar egreso fijo'))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(tags=['Egresos'], operation_summary='Actualizar parcialmente egreso fijo'))
@method_decorator(name='destroy', decorator=swagger_auto_schema(tags=['Egresos'], operation_summary='Eliminar egreso fijo'))
class EgresosFijosApiViewSet(ModelViewSet):
    # ViewSet for Egresos Fijos
    serializer_class = EgresosFijosSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name', 'quantity', 'period']

    def get_queryset(self):
        user = getattr(self.request, 'user', None)
        if not user or not user.is_authenticated:
            return EgresosFijos.objects.none()
        return EgresosFijos.objects.filter(owner=user).order_by('-id')

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

@method_decorator(name='list', decorator=swagger_auto_schema(tags=['Egresos'], operation_summary='Listar egresos extra', responses={200: EgresosExtraSerializer(many=True)}))
@method_decorator(name='create', decorator=swagger_auto_schema(tags=['Egresos'], operation_summary='Crear egreso extra', request_body=openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['name','reason','quantity','date'],
    properties={
        'name': openapi.Schema(type=openapi.TYPE_STRING, example='Comida'),
        'reason': openapi.Schema(type=openapi.TYPE_STRING, example='Restaurante'),
        'quantity': openapi.Schema(type=openapi.TYPE_STRING, example='25.00'),
        'date': openapi.Schema(type=openapi.TYPE_STRING, example='2025-08-28')
    }
)))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(tags=['Egresos'], operation_summary='Detalle de egreso extra'))
@method_decorator(name='update', decorator=swagger_auto_schema(tags=['Egresos'], operation_summary='Actualizar egreso extra'))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(tags=['Egresos'], operation_summary='Actualizar parcialmente egreso extra'))
@method_decorator(name='destroy', decorator=swagger_auto_schema(tags=['Egresos'], operation_summary='Eliminar egreso extra'))
class EgresosExtraApiViewSet(ModelViewSet):
    # ViewSet for Egresos Extra
    serializer_class = EgresosExtraSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name', 'quantity', 'date']

    def get_queryset(self):
        user = getattr(self.request, 'user', None)
        if not user or not user.is_authenticated:
            return EgresosExtra.objects.none()
        return EgresosExtra.objects.filter(owner=user).order_by('-date', '-id')

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
