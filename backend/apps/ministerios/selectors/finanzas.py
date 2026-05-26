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


def resumen_ofrendas_por_clase(ministry: Ministerio, mes: int = None, anio: int = None):
    queryset = ministry.ofrendas.filter(aprobado=True)
    if mes:
        queryset = queryset.filter(fecha__month=mes)
    if anio:
        queryset = queryset.filter(fecha__year=anio)
    resultados = queryset.values('clase').annotate(
        total=Sum('monto')
    )
    return [
        {
            'clase': r['clase'] or 'sin_clase',
            'total': float(r['total']),
            'count': queryset.filter(clase=r['clase']).count(),
        }
        for r in resultados if r['clase']
    ]


def resumen_ofrendas_por_categoria(ministry: Ministerio, mes: int = None, anio: int = None):
    queryset = ministry.ofrendas.filter(aprobado=True)
    if mes:
        queryset = queryset.filter(fecha__month=mes)
    if anio:
        queryset = queryset.filter(fecha__year=anio)
    resultados = queryset.values('categoria').annotate(
        total=Sum('monto')
    )
    return [
        {
            'categoria': r['categoria'] or 'sin_categoria',
            'total': float(r['total'] or 0),
            'count': queryset.filter(categoria=r['categoria']).count(),
        }
        for r in resultados if r['categoria']
    ]


def reporte_ofrendas_por_periodo(ministry: Ministerio, fecha_inicio, fecha_fin):
    queryset = ministry.ofrendas.filter(
        fecha__gte=fecha_inicio,
        fecha__lte=fecha_fin,
        aprobado=True
    )
    resultados = queryset.values('categoria').annotate(
        total=Sum('monto')
    )
    detalle = []
    for r in resultados:
        if r['categoria']:
            detalle.append({
                'categoria': r['categoria'],
                'total': float(r['total'] or 0),
                'count': queryset.filter(categoria=r['categoria']).count(),
            })
    total_general = float(queryset.aggregate(total=Sum('monto'))['total'] or 0)
    return {
        'fecha_inicio': str(fecha_inicio),
        'fecha_fin': str(fecha_fin),
        'total_general': total_general,
        'por_categoria': detalle,
    }
