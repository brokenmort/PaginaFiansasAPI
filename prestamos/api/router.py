from rest_framework.routers import DefaultRouter
from prestamos.api.views import PrestamosApiViewSet

# Create a router and register our viewset with it.
router_prestamos = DefaultRouter()
# Register the CategoryApiViewSet with the router
router_prestamos.register(prefix='prestamos', basename='prestamos', viewset=PrestamosApiViewSet)
# The router will automatically generate the necessary URL patterns for the PrestamosApiViewSet
