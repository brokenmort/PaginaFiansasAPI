from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from prestamos.models import Prestamos
from prestamos.api.serializers import PrestamosSerializer

@method_decorator(name='list', decorator=swagger_auto_schema(tags=['Prestamos'], operation_summary='Listar préstamos'))
@method_decorator(name='create', decorator=swagger_auto_schema(tags=['Prestamos'], operation_summary='Crear préstamo', request_body=openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['name','reason','quantity','payment','period'],
    properties={
        'name': openapi.Schema(type=openapi.TYPE_STRING, example='Préstamo personal'),
        'reason': openapi.Schema(type=openapi.TYPE_STRING, example='Compra'),
        'quantity': openapi.Schema(type=openapi.TYPE_STRING, example='3000.00'),
        'payment': openapi.Schema(type=openapi.TYPE_STRING, example='150.00'),
        'period': openapi.Schema(type=openapi.TYPE_STRING, example='Mensual'),
        'status': openapi.Schema(type=openapi.TYPE_STRING, example='Pendiente'),
        'answer': openapi.Schema(type=openapi.TYPE_STRING, example='Favorable')
    }
)))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(tags=['Prestamos'], operation_summary='Detalle de un préstamo'))
@method_decorator(name='update', decorator=swagger_auto_schema(tags=['Prestamos'], operation_summary='Actualizar préstamo'))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(tags=['Prestamos'], operation_summary='Actualizar parcialmente préstamo'))
@method_decorator(name='destroy', decorator=swagger_auto_schema(tags=['Prestamos'], operation_summary='Eliminar préstamo'))
class PrestamosApiViewSet(ModelViewSet):
   # API endpoint that allows prestamos to be viewed or edited.
   serializer_class = PrestamosSerializer
   permission_classes = [IsAuthenticated]

   def get_queryset(self):
       user = getattr(self.request, 'user', None)
       if not user or not user.is_authenticated:
           return Prestamos.objects.none()
       return Prestamos.objects.filter(owner=user).order_by('-id')

   def perform_create(self, serializer):
       serializer.save(owner=self.request.user)
