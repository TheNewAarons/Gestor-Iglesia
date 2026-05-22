from django.db.models import Sum, Q
from apps.ministerios.models import Ministerio, CajaMinisterio, MovimientoCaja, Ofrenda
from ..models import ConfiguracionFinanzas, InformeMensual


def saldos_ministerios():
    """Retorna saldos de cajas de todos los ministerios activos."""
    cajas = CajaMinisterio.objects.select_related('ministry').filter(
        ministry__activo=True
    ).annotate(
        total_ingresos=Sum('movimientos__monto', filter=Q(movimientos__tipo='ingreso')),
        total_egresos=Sum('movimientos__monto', filter=Q(movimientos__tipo='egreso')),
    )
    resultados = []
    for caja in cajas:
        ingresos = caja.total_ingresos or 0
        egresos = caja.total_egresos or 0
        resultados.append({
            'ministry_slug': caja.ministry.slug,
            'ministry_nombre': caja.ministry.nombre,
            'ministry_color': caja.ministry.color,
            'saldo': float(ingresos - egresos),
            'total_ingresos': float(ingresos),
            'total_egresos': float(egresos),
        })
    return resultados


def consolidar_flujo_caja(mes, anio):
    """Consolida el flujo de caja mensual: ingresos y egresos por categoría."""
    ingresos = Ofrenda.objects.filter(fecha__year=anio, fecha__month=mes).aggregate(
        total=Sum('monto')
    )['total'] or 0

    egresos_movimientos = MovimientoCaja.objects.filter(
        fecha__year=anio, fecha__month=mes, tipo='egreso'
    )
    total_egresos = egresos_movimientos.aggregate(total=Sum('monto'))['total'] or 0

    movimientos_ingreso = MovimientoCaja.objects.filter(
        fecha__year=anio, fecha__month=mes, tipo='ingreso'
    )
    total_ingresos_caja = movimientos_ingreso.aggregate(total=Sum('monto'))['total'] or 0

    return {
        'mes': mes,
        'anio': anio,
        'total_ofrendas': float(ingresos),
        'total_ingresos_caja': float(total_ingresos_caja),
        'total_egresos': float(total_egresos),
        'saldo_neto': float(total_ingresos_caja) + float(ingresos) - float(total_egresos),
    }


def configuracion_actual():
    """Retorna la configuración de finanzas vigente."""
    return ConfiguracionFinanzas.obtener()


def informes_mensuales():
    """Retorna todos los informes mensuales generados."""
    return InformeMensual.objects.all()


def obtener_informe(anio, mes):
    """Retorna un informe específico o None."""
    try:
        return InformeMensual.objects.get(anio=anio, mes=mes)
    except InformeMensual.DoesNotExist:
        return None


def listar_boletas_egresos(fecha_inicio=None, fecha_fin=None):
    """Lista boletas (imágenes) de egresos de todos los ministerios."""
    qs = MovimientoCaja.objects.filter(
        tipo='egreso', imagen__isnull=False
    ).exclude(imagen='').select_related('caja__ministry', 'registrado_por')

    if fecha_inicio:
        qs = qs.filter(fecha__date__gte=fecha_inicio)
    if fecha_fin:
        qs = qs.filter(fecha__date__lte=fecha_fin)

    return qs.order_by('-fecha')


def listar_traspasos():
    """Lista movimientos marcados como enviados a tesorería."""
    return MovimientoCaja.objects.filter(
        enviado_tesoreria=True
    ).select_related('caja__ministry', 'registrado_por').order_by('-fecha')
