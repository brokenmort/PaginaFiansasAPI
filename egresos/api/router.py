from rest_framework.routers import DefaultRouter
from egresos.api.views import EgresosFijosApiViewSet, EgresosExtraApiViewSet


# Create a router and register our viewsets with it.

router_EgresosFijos = DefaultRouter()
router_EgresosFijos.register(prefix='EgresosFijos', basename='EgresosFijos', viewset=EgresosFijosApiViewSet)

router_EgresosExtra = DefaultRouter()
router_EgresosExtra.register(prefix='EgresosExtra', basename='EgresosExtra', viewset=EgresosExtraApiViewSet)
# The API URLs are now determined automatically by the router.

