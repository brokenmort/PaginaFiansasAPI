# web/urls.py
from django.contrib import admin
from django.urls import path, include, re_path
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static

from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

# Routers de las apps
from ingresos.api.router import router_IngresosFijos, router_IngresosExtra
from egresos.api.router import router_EgresosFijos, router_EgresosExtra
from ahorros.api.router import router_ahorros
from prestamos.api.router import router_prestamos
from reports.api.views import SummaryView, CashflowMonthlyView

schema_view = get_schema_view(
    openapi.Info(
        title="Finansas API",
        default_version='v1',
        description="Documentación de la API de Finansas",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    authentication_classes=(),
)

def redirect_to_docs(request):
    # Al abrir la raíz "/", te manda a Swagger UI
    return redirect('/docs/')

urlpatterns = [
    path('', redirect_to_docs, name='root'),
    path('admin/', admin.site.urls),

    # Tus endpoints
    path('api/', include('users.api.router')),
    path('api/', include(router_IngresosFijos.urls)),
    path('api/', include(router_IngresosExtra.urls)),
    path('api/', include(router_EgresosFijos.urls)),
    path('api/', include(router_EgresosExtra.urls)),
    path('api/', include(router_ahorros.urls)),
    path('api/', include(router_prestamos.urls)),
    path('api/reports/summary/', SummaryView.as_view(), name='reports-summary'),
    path('api/reports/cashflow/monthly/', CashflowMonthlyView.as_view(), name='reports-cashflow-monthly'),

    # Login/Logout para la vista de Swagger (drf-yasg)
    path('api-auth/', include('rest_framework.urls')),

    # Documentación
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),

]

# Servir archivos de media (profile_image) también en producción (Heroku)
# Nota: Para alto tráfico, usar almacenamiento externo (S3/Cloudinary).
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
