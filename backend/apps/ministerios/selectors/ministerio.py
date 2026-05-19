from django.db.models import Count, Q, Sum
from datetime import date
from ..models import Ministerio


def listar_ministerios(activos: bool = True):
    """Lista todos los ministerios con conteo de miembros activos"""
    queryset = Ministerio.objects.annotate(
        miembros_count=Count('miembros', filter=Q(miembros__activo=True))
    ).prefetch_related('lideres')
    if activos:
        queryset = queryset.filter(activo=True)
    return queryset


def obtener_ministerio_por_slug(slug: str):
    """Obtiene un ministerio por slug con datos relacionados"""
    try:
        return Ministerio.objects.annotate(
            miembros_count=Count('miembros', filter=Q(miembros__activo=True))
        ).prefetch_related('lideres').get(slug=slug)
    except Ministerio.DoesNotExist:
        return None


def obtener_dashboard(ministry: Ministerio) -> dict:
    """Datos del dashboard de un ministerio"""
    miembros_count = ministry.miembros.filter(activo=True).count()

    caja = getattr(ministry, 'caja', None)
    saldo_caja = caja.calcular_saldo() if caja else 0

    eventos_proximos = ministry.eventos.filter(
        fecha_inicio__gte=date.today()
    ).order_by('fecha_inicio')[:5]

    ofertas_mes = ministry.ofrendas.filter(
        fecha__month=date.today().month,
        fecha__year=date.today().year
    ).aggregate(total=Sum('monto'))['total'] or 0

    return {
        'miembros_count': miembros_count,
        'saldo_caja': float(saldo_caja),
        'ofertas_mes': float(ofertas_mes),
        'eventos_proximos': list(eventos_proximos),
        'miembros_recientes': list(
            ministry.miembros.filter(activo=True).select_related('usuario')[:10]
        ),
    }
