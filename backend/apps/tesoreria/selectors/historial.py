from django.db.models import Q
from apps.ministerios.models import MovimientoCaja
from ..models import MovimientoTesoreria, HistorialLog


def _normalizar_historial_log(log):
    return {
        'id': f'log_{log.id}',
        'fuente': 'auditoria',
        'fuente_label': 'Registro',
        'fecha': log.fecha.isoformat() if hasattr(log.fecha, 'isoformat') else str(log.fecha),
        'tipo': 'ingreso' if log.accion != 'eliminado' else 'neutral',
        'tipo_label': log.get_accion_display(),
        'accion': log.accion,
        'entidad_tipo': log.entidad_tipo,
        'entidad_id': log.entidad_id,
        'ministry_nombre': log.ministry.nombre if log.ministry else None,
        'ministry_slug': log.ministry.slug if log.ministry else None,
        'ministry_color': log.ministry.color if log.ministry else None,
        'monto': 0,
        'descripcion': log.resumen or '',
        'imagen': None,
        'imagen_url': None,
        'registrado_por_nombre': log.usuario.get_full_name() or log.usuario.username if log.usuario else None,
    }


def _normalizar_movimiento_caja(m):
    return {
        'id': f'caja_{m.id}',
        'fuente': 'caja_ministerio',
        'fuente_label': 'Caja Ministerio',
        'fecha': m.fecha.isoformat() if hasattr(m.fecha, 'isoformat') else str(m.fecha),
        'tipo': m.tipo,
        'tipo_label': 'Ingreso' if m.tipo == 'ingreso' else 'Egreso',
        'ministry_nombre': m.caja.ministry.nombre if m.caja and m.caja.ministry else None,
        'ministry_slug': m.caja.ministry.slug if m.caja and m.caja.ministry else None,
        'ministry_color': m.caja.ministry.color if m.caja and m.caja.ministry else None,
        'monto': float(m.monto),
        'descripcion': m.descripcion or '',
        'imagen': None,
        'imagen_url': None,
        'registrado_por_nombre': m.registrado_por.get_full_name() or m.registrado_por.username if m.registrado_por else None,
    }


def _normalizar_movimiento_tesoreria(m, request=None):
    imagen_url = None
    if m.imagen and request:
        imagen_url = request.build_absolute_uri(m.imagen.url)

    TIPO_LABELS = {
        'ingreso_diezmo': 'Diezmo',
        'ingreso_especial': 'Donación Especial',
        'ingreso_ofrenda': 'Ofrenda',
        'ingreso_ahorro': 'Ahorro',
        'ingreso_proyectos': 'Proyectos',
        'egreso_sosten_pastoral': 'Sosten Pastoral',
        'egreso_beneficios_pastorales': 'Beneficios Pastorales',
        'egreso_varios_iglesia': 'Gastos Varios Iglesia',
        'egreso_fondo_contingencia': 'Fondo de Contingencia',
    }

    return {
        'id': f'tes_{m.id}',
        'fuente': 'tesoreria_central',
        'fuente_label': 'Tesorería Central',
        'fecha': m.fecha.isoformat() if hasattr(m.fecha, 'isoformat') else str(m.fecha),
        'tipo': 'ingreso' if m.tipo.startswith('ingreso') else 'egreso',
        'tipo_label': TIPO_LABELS.get(m.tipo, m.tipo),
        'tipo_tesoreria': m.tipo,
        'ministry_nombre': m.ministry.nombre if m.ministry else None,
        'ministry_slug': m.ministry.slug if m.ministry else None,
        'ministry_color': m.ministry.color if m.ministry else None,
        'monto': float(m.monto),
        'descripcion': m.descripcion or '',
        'imagen': m.imagen.name if m.imagen else None,
        'imagen_url': imagen_url,
        'registrado_por_nombre': m.registrado_por.get_full_name() or m.registrado_por.username if m.registrado_por else None,
    }


def listar_historial(fecha_inicio=None, fecha_fin=None, ministry_slug=None, tipo=None):
    resultados = []

    caja_qs = MovimientoCaja.objects.select_related('caja__ministry', 'registrado_por').filter(aprobado=True)
    if fecha_inicio:
        caja_qs = caja_qs.filter(fecha__date__gte=fecha_inicio)
    if fecha_fin:
        caja_qs = caja_qs.filter(fecha__date__lte=fecha_fin)
    if ministry_slug:
        caja_qs = caja_qs.filter(caja__ministry__slug=ministry_slug)
    if tipo:
        if tipo == 'ingreso':
            caja_qs = caja_qs.filter(tipo='ingreso')
        elif tipo == 'egreso':
            caja_qs = caja_qs.filter(tipo='egreso')

    for m in caja_qs.order_by('-fecha', '-id'):
        resultados.append(_normalizar_movimiento_caja(m))

    tes_qs = MovimientoTesoreria.objects.select_related('ministry', 'registrado_por').all()
    if fecha_inicio:
        tes_qs = tes_qs.filter(fecha__gte=fecha_inicio)
    if fecha_fin:
        tes_qs = tes_qs.filter(fecha__lte=fecha_fin)
    if ministry_slug:
        tes_qs = tes_qs.filter(ministry__slug=ministry_slug)
    if tipo:
        if tipo == 'ingreso':
            tes_qs = tes_qs.filter(tipo__startswith='ingreso')
        elif tipo == 'egreso':
            tes_qs = tes_qs.filter(tipo__startswith='egreso')

    for m in tes_qs.order_by('-fecha', '-id'):
        resultados.append(_normalizar_movimiento_tesoreria(m))

    log_qs = HistorialLog.objects.select_related('ministry', 'usuario').all()
    if fecha_inicio:
        log_qs = log_qs.filter(fecha__date__gte=fecha_inicio)
    if fecha_fin:
        log_qs = log_qs.filter(fecha__date__lte=fecha_fin)
    if ministry_slug:
        log_qs = log_qs.filter(ministry__slug=ministry_slug)

    for log in log_qs.order_by('-fecha', '-id'):
        resultados.append(_normalizar_historial_log(log))

    resultados.sort(key=lambda x: (x['fecha'], x['id']), reverse=True)
    return resultados
