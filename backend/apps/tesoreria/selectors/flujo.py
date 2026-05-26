from django.db.models import Sum, Q
from apps.ministerios.models import Ministerio, CajaMinisterio, MovimientoCaja, Ofrenda
from ..models import ConfiguracionFinanzas, InformeMensual, MovimientoTesoreria, CuotaFija


def saldos_ministerios():
    """Retorna saldos de cajas de todos los ministerios activos."""
    cajas = CajaMinisterio.objects.select_related('ministry').filter(
        ministry__activo=True
    ).annotate(
        total_ingresos=Sum('movimientos__monto', filter=Q(movimientos__tipo='ingreso', movimientos__aprobado=True)),
        total_egresos=Sum('movimientos__monto', filter=Q(movimientos__tipo='egreso', movimientos__aprobado=True)),
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
    """Consolida el flujo de caja mensual: ingresos y egresos por categoria."""
    ingresos = Ofrenda.objects.filter(fecha__year=anio, fecha__month=mes, aprobado=True).aggregate(
        total=Sum('monto')
    )['total'] or 0

    egresos_movimientos = MovimientoCaja.objects.filter(
        fecha__year=anio, fecha__month=mes, tipo='egreso', aprobado=True
    )
    total_egresos = egresos_movimientos.aggregate(total=Sum('monto'))['total'] or 0

    movimientos_ingreso = MovimientoCaja.objects.filter(
        fecha__year=anio, fecha__month=mes, tipo='ingreso', aprobado=True
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
    return ConfiguracionFinanzas.obtener()


def informes_mensuales():
    return InformeMensual.objects.all()


def obtener_informe(anio, mes):
    try:
        return InformeMensual.objects.get(anio=anio, mes=mes)
    except InformeMensual.DoesNotExist:
        return None


def listar_boletas_egresos(fecha_inicio=None, fecha_fin=None):
    qs = MovimientoCaja.objects.filter(
        imagen__isnull=False, aprobado=True
    ).exclude(imagen='').select_related('caja__ministry', 'registrado_por')

    if fecha_inicio:
        qs = qs.filter(fecha__date__gte=fecha_inicio)
    if fecha_fin:
        qs = qs.filter(fecha__date__lte=fecha_fin)

    return qs.order_by('-fecha')


def listar_traspasos():
    return MovimientoCaja.objects.filter(
        enviado_tesoreria=True, aprobado=True
    ).select_related('caja__ministry', 'registrado_por').order_by('-fecha')


def listar_movimientos_tesoreria(tipo=None):
    qs = MovimientoTesoreria.objects.select_related('registrado_por')
    if tipo:
        qs = qs.filter(tipo=tipo)
    return qs


def listar_cuotas_fijas():
    return CuotaFija.objects.select_related('ministry').all()


def obtener_informe_mes_anterior(anio, mes):
    if mes == 1:
        anio_ant = anio - 1
        mes_ant = 12
    else:
        anio_ant = anio
        mes_ant = mes - 1
    try:
        return InformeMensual.objects.get(anio=anio_ant, mes=mes_ant)
    except InformeMensual.DoesNotExist:
        return None


def ofrendas_por_categoria_mni(mes, anio):
    """Retorna total de ofrendas MNI agrupadas por categoria."""
    ofrendas = Ofrenda.objects.filter(
        ministry__slug='mni', fecha__year=anio, fecha__month=mes, aprobado=True
    )
    total_general = ofrendas.filter(categoria='ofrenda_general').aggregate(t=Sum('monto'))['t'] or 0
    caja_alabastro = ofrendas.filter(categoria='caja_alabastro').aggregate(t=Sum('monto'))['t'] or 0
    accion_gracias = ofrendas.filter(categoria='accion_gracias').aggregate(t=Sum('monto'))['t'] or 0
    dip = ofrendas.filter(categoria='dip').aggregate(t=Sum('monto'))['t'] or 0
    oracion_ayuno = ofrendas.filter(categoria='oracion_ayuno').aggregate(t=Sum('monto'))['t'] or 0
    fem = ofrendas.filter(categoria='fem').aggregate(t=Sum('monto'))['t'] or 0
    otros = ofrendas.filter(categoria='otros').aggregate(t=Sum('monto'))['t'] or 0
    sin_categoria = ofrendas.filter(categoria='').aggregate(t=Sum('monto'))['t'] or 0
    return {
        'ofrenda_general': float(total_general) + float(sin_categoria),
        'caja_alabastro': float(caja_alabastro),
        'accion_gracias': float(accion_gracias),
        'dip': float(dip),
        'oracion_ayuno': float(oracion_ayuno),
        'fem': float(fem),
        'otros': float(otros),
        'total': float((total_general + caja_alabastro + accion_gracias + dip + oracion_ayuno + fem + otros + sin_categoria)),
    }
