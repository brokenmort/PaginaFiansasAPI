from rest_framework.viewsets import ModelViewSet  # CRUD base
from rest_framework.permissions import IsAuthenticated  # Require JWT auth
from django_filters.rest_framework import DjangoFilterBackend  # Filtering support
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from ingresos.models import IngresosFijos, IngresosExtra  # ORM models
from ingresos.api.serializers import IngresosFijosSerializer, IngresosExtraSerializer  # Serializers


@method_decorator(name='list', decorator=swagger_auto_schema(tags=['Ingresos'], operation_summary='Listar ingresos fijos', responses={200: IngresosFijosSerializer(many=True)}))
@method_decorator(name='create', decorator=swagger_auto_schema(tags=['Ingresos'], operation_summary='Crear ingreso fijo', request_body=openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['name','reason','quantity'],
    properties={
        'name': openapi.Schema(type=openapi.TYPE_STRING, example='Salario'),
        'reason': openapi.Schema(type=openapi.TYPE_STRING, example='Pago mensual'),
        'quantity': openapi.Schema(type=openapi.TYPE_STRING, example='1000.00'),
        'period': openapi.Schema(type=openapi.TYPE_STRING, example='Mensual')
    }
)))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(tags=['Ingresos'], operation_summary='Detalle de ingreso fijo'))
@method_decorator(name='update', decorator=swagger_auto_schema(tags=['Ingresos'], operation_summary='Actualizar ingreso fijo'))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(tags=['Ingresos'], operation_summary='Actualizar parcialmente ingreso fijo'))
@method_decorator(name='destroy', decorator=swagger_auto_schema(tags=['Ingresos'], operation_summary='Eliminar ingreso fijo'))
class IngresosFijosApiViewSet(ModelViewSet):
   # Fixed incomes endpoints
   serializer_class = IngresosFijosSerializer
   permission_classes = [IsAuthenticated]
   filter_backends = [DjangoFilterBackend]
   filterset_fields = ['name', 'quantity', 'period']

   def get_queryset(self):
       # Only records belonging to the current user
       user = getattr(self.request, 'user', None)
       if not user or not user.is_authenticated:
           return IngresosFijos.objects.none()
       return IngresosFijos.objects.filter(owner=user).order_by('-id')

   def perform_create(self, serializer):
       # Set logged-in user as owner on create
       serializer.save(owner=self.request.user)

@method_decorator(name='list', decorator=swagger_auto_schema(tags=['Ingresos'], operation_summary='Listar ingresos extra', responses={200: IngresosExtraSerializer(many=True)}))
@method_decorator(name='create', decorator=swagger_auto_schema(tags=['Ingresos'], operation_summary='Crear ingreso extra', request_body=openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['name','reason','quantity','date'],
    properties={
        'name': openapi.Schema(type=openapi.TYPE_STRING, example='Freelance'),
        'reason': openapi.Schema(type=openapi.TYPE_STRING, example='Proyecto web'),
        'quantity': openapi.Schema(type=openapi.TYPE_STRING, example='250.50'),
        'date': openapi.Schema(type=openapi.TYPE_STRING, example='2025-08-28')
    }
)))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(tags=['Ingresos'], operation_summary='Detalle de ingreso extra'))
@method_decorator(name='update', decorator=swagger_auto_schema(tags=['Ingresos'], operation_summary='Actualizar ingreso extra'))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(tags=['Ingresos'], operation_summary='Actualizar parcialmente ingreso extra'))
@method_decorator(name='destroy', decorator=swagger_auto_schema(tags=['Ingresos'], operation_summary='Eliminar ingreso extra'))
class IngresosExtraApiViewSet(ModelViewSet):
   # Extra incomes endpoints
   serializer_class = IngresosExtraSerializer
   permission_classes = [IsAuthenticated]
   filter_backends = [DjangoFilterBackend]
   filterset_fields = ['name', 'quantity', 'date']

   def get_queryset(self):
       # Only records belonging to the current user
       user = getattr(self.request, 'user', None)
       if not user or not user.is_authenticated:
           return IngresosExtra.objects.none()
       return IngresosExtra.objects.filter(owner=user).order_by('-date', '-id')

   def perform_create(self, serializer):
       # Set logged-in user as owner on create
       serializer.save(owner=self.request.user)
