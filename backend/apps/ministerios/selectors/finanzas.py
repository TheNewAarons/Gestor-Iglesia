from django.db.models import Sum
from ..models import CajaMinisterio, MovimientoCaja, Ofrenda, Ministerio


def obtener_caja(ministry: Ministerio):
    """Obtiene la caja de un ministerio con sus movimientos"""
    try:
        return CajaMinisterio.objects.prefetch_related(
            'movimientos'
        ).get(ministry=ministry)
    except CajaMinisterio.DoesNotExist:
        return None


def listar_movimientos(caja: CajaMinisterio, filters: dict = None):
    """Lista movimientos de caja con filtros"""
    queryset = caja.movimientos.select_related('registrado_por')
    if filters:
        if tipo := filters.get('tipo'):
            queryset = queryset.filter(tipo=tipo)
        if enviado_tesoreria := filters.get('enviado_tesoreria'):
            queryset = queryset.filter(enviado_tesoreria=enviado_tesoreria)
    return queryset


def listar_ofrendas(ministry: Ministerio, filters: dict = None):
    """Lista ofrendas de un ministerio con filtros de fecha"""
    queryset = ministry.ofrendas.all()
    if filters:
        if fecha_inicio := filters.get('fecha_inicio'):
            queryset = queryset.filter(fecha__gte=fecha_inicio)
        if fecha_fin := filters.get('fecha_fin'):
            queryset = queryset.filter(fecha__lte=fecha_fin)
    return queryset


def total_ofrendas_mes(ministry: Ministerio, mes: int, anio: int):
    """Calcula el total de ofrendas de un mes"""
    return ministry.ofrendas.filter(
        fecha__month=mes,
        fecha__year=anio,
        aprobado=True
    ).aggregate(total=Sum('monto'))['total'] or 0
