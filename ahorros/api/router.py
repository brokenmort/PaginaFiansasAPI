from rest_framework.routers import DefaultRouter
from ahorros.api.views import AhorrosApiViewSet

router_ahorros = DefaultRouter()
# Register the CategoryApiViewSet with the router
router_ahorros.register(prefix='ahorros', basename='ahorros', viewset=AhorrosApiViewSet)
# The router will automatically generate the necessary URL patterns for the CategoryApiViewSet
