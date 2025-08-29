from datetime import date  # Standard date type
from django.utils.dateparse import parse_date  # Safe parse from 'YYYY-MM-DD'
from django.db import models  # Aggregations (Sum)
from rest_framework.views import APIView  # Base API view
from rest_framework.response import Response  # JSON responses
from rest_framework.permissions import IsAuthenticated  # Require auth
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ingresos.models import IngresosFijos, IngresosExtra  # Income models
from egresos.models import EgresosFijos, EgresosExtra  # Expense models
from ahorros.models import Ahorros  # Savings model
from prestamos.models import Prestamos  # Loans model


class SummaryView(APIView):
    # Returns numeric totals and net balance for the user
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary='Resumen general',
        tags=['Reportes'],
        manual_parameters=[
            openapi.Parameter('start', openapi.IN_QUERY, description='YYYY-MM-DD', type=openapi.TYPE_STRING),
            openapi.Parameter('end', openapi.IN_QUERY, description='YYYY-MM-DD', type=openapi.TYPE_STRING),
        ],
        responses={200: openapi.Response('OK', examples={'application/json': {
            'period': {'start': None, 'end': None},
            'ingresos': {'fijos': 2000.0, 'extra': 501.0, 'total': 2501.0},
            'egresos': {'fijos': 1000.0, 'extra': 240.0, 'total': 1240.0},
            'balanza_neta': 1261.0,
            'ahorros': {'objetivo_total': 4000.0, 'acumulado_total': 0.0},
            'prestamos': {'monto_total': 6000.0}
        }})}
    )
    def get(self, request):
        """
        Devuelve sumas por categoría y balance neto.
        Query params opcionales: start=YYYY-MM-DD, end=YYYY-MM-DD
        Nota: los registros Fijos no tienen fecha; se cuentan completos.
        """
        # Parse optional range params (apply to records with date)
        start_param = request.query_params.get('start')
        end_param = request.query_params.get('end')
        start = parse_date(start_param) if start_param else None
        end = parse_date(end_param) if end_param else None

        user = request.user

        # Incomes
        q_if = IngresosFijos.objects.filter(owner=user)
        q_ie = IngresosExtra.objects.filter(owner=user)
        if start:
            q_ie = q_ie.filter(date__gte=start)
        if end:
            q_ie = q_ie.filter(date__lte=end)

        ingresos_fijos_total = q_if.aggregate(total=models.Sum('quantity'))['total'] or 0
        ingresos_extra_total = q_ie.aggregate(total=models.Sum('quantity'))['total'] or 0

        # Expenses
        q_ef = EgresosFijos.objects.filter(owner=user)
        q_ee = EgresosExtra.objects.filter(owner=user)
        if start:
            q_ee = q_ee.filter(date__gte=start)
        if end:
            q_ee = q_ee.filter(date__lte=end)

        egresos_fijos_total = q_ef.aggregate(total=models.Sum('quantity'))['total'] or 0
        egresos_extra_total = q_ee.aggregate(total=models.Sum('quantity'))['total'] or 0

        # Savings and loans (simple totals)
        ahorros_total_objetivo = Ahorros.objects.filter(owner=user).aggregate(total=models.Sum('quantity'))['total'] or 0
        ahorros_total_acumulado = Ahorros.objects.filter(owner=user).aggregate(total=models.Sum('accrued'))['total'] or 0
        prestamos_total = Prestamos.objects.filter(owner=user).aggregate(total=models.Sum('quantity'))['total'] or 0

        neto = (ingresos_fijos_total + ingresos_extra_total) - (egresos_fijos_total + egresos_extra_total)

        # Serialize floats for JSON
        return Response({
            'period': {'start': start, 'end': end},
            'ingresos': {
                'fijos': float(ingresos_fijos_total),
                'extra': float(ingresos_extra_total),
                'total': float(ingresos_fijos_total + ingresos_extra_total),
            },
            'egresos': {
                'fijos': float(egresos_fijos_total),
                'extra': float(egresos_extra_total),
                'total': float(egresos_fijos_total + egresos_extra_total),
            },
            'balanza_neta': float(neto),
            'ahorros': {
                'objetivo_total': float(ahorros_total_objetivo),
                'acumulado_total': float(ahorros_total_acumulado),
            },
            'prestamos': {
                'monto_total': float(prestamos_total),
            },
        })


from django.db.models.functions import TruncMonth  # Group by month


class CashflowMonthlyView(APIView):
    # Monthly sums for extra incomes/expenses
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary='Flujo mensual (extra)',
        tags=['Reportes'],
        manual_parameters=[
            openapi.Parameter('start', openapi.IN_QUERY, description='YYYY-MM-DD', type=openapi.TYPE_STRING),
            openapi.Parameter('end', openapi.IN_QUERY, description='YYYY-MM-DD', type=openapi.TYPE_STRING),
        ],
        responses={200: openapi.Response('OK', examples={'application/json': {
            'range': {'start': None, 'end': None},
            'months': [
                {'month': '2025-08-01', 'ingresos_extra': 501.0, 'egresos_extra': 240.0, 'neto_extra': 261.0}
            ]
        }})}
    )
    def get(self, request):
        """
        Devuelve sumas mensuales de ingresos/egresos EXTRA (por fecha).
        Params opcionales: start=YYYY-MM-DD, end=YYYY-MM-DD
        """
        start_param = request.query_params.get('start')
        end_param = request.query_params.get('end')
        start = parse_date(start_param) if start_param else None
        end = parse_date(end_param) if end_param else None

        user = request.user

        q_ie = IngresosExtra.objects.filter(owner=user)
        q_ee = EgresosExtra.objects.filter(owner=user)
        if start:
            q_ie = q_ie.filter(date__gte=start)
            q_ee = q_ee.filter(date__gte=start)
        if end:
            q_ie = q_ie.filter(date__lte=end)
            q_ee = q_ee.filter(date__lte=end)

        ie = (
            q_ie.annotate(month=TruncMonth('date'))
               .values('month')
               .annotate(total=models.Sum('quantity'))
               .order_by('month')
        )
        ee = (
            q_ee.annotate(month=TruncMonth('date'))
               .values('month')
               .annotate(total=models.Sum('quantity'))
               .order_by('month')
        )

        # Normalizamos a { 'YYYY-MM-01': { ingresos_extra, egresos_extra } }
        from collections import defaultdict  # Accumulate monthly data
        out = defaultdict(lambda: {'ingresos_extra': 0.0, 'egresos_extra': 0.0})
        for row in ie:
            key = row['month'].strftime('%Y-%m-01')
            out[key]['ingresos_extra'] = float(row['total'] or 0)
        for row in ee:
            key = row['month'].strftime('%Y-%m-01')
            out[key]['egresos_extra'] = float(row['total'] or 0)

        # A lista ordenada
        result = [
            {'month': k, **v, 'neto_extra': round(v['ingresos_extra'] - v['egresos_extra'], 2)}
            for k, v in sorted(out.items())
        ]
        return Response({'range': {'start': start, 'end': end}, 'months': result})
