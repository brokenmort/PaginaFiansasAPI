from rest_framework.routers import DefaultRouter
from ingresos.api.views import IngresosFijosApiViewSet, IngresosExtraApiViewSet

# Create a router and register our viewsets with it.

router_IngresosFijos = DefaultRouter()
router_IngresosFijos.register(prefix='IngresosFijos', basename='IngresosFijos', viewset=IngresosFijosApiViewSet)

router_IngresosExtra = DefaultRouter()
router_IngresosExtra.register(prefix='IngresosExtra', basename='IngresosExtra', viewset=IngresosExtraApiViewSet)
# The API URLs are now determined automatically by the router.

