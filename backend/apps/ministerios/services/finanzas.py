from django.db import transaction
from django.utils import timezone
from ..models import CajaMinisterio, MovimientoCaja, Ofrenda
from apps.tesoreria.models import MovimientoTesoreria, HistorialLog


@transaction.atomic
def obtener_o_crear_caja(ministry) -> CajaMinisterio:
    """Obtiene o crea una caja para un ministerio"""
    caja, _ = CajaMinisterio.objects.get_or_create(ministry=ministry)
    return caja


@transaction.atomic
def crear_movimiento(caja: CajaMinisterio, registrado_por, **kwargs) -> MovimientoCaja:
    """Registra un movimiento de caja (ingreso/egreso)"""
    movimiento = MovimientoCaja.objects.create(
        caja=caja, registrado_por=registrado_por, **kwargs
    )
    HistorialLog.objects.create(
        entidad_tipo='movimiento_caja',
        entidad_id=movimiento.id,
        accion='creado',
        resumen=f'{movimiento.get_tipo_display()} {movimiento.monto} — {caja.ministry.nombre}',
        ministry=caja.ministry,
        usuario=registrado_por,
    )
    return movimiento


@transaction.atomic
def crear_ofrenda(ministry, usuario, **kwargs) -> Ofrenda:
    """Registra una ofrenda (pendiente de aprobación por tesorería)"""
    ofrenda = Ofrenda.objects.create(ministry=ministry, **kwargs)
    HistorialLog.objects.create(
        entidad_tipo='ofrenda',
        entidad_id=ofrenda.id,
        accion='creado',
        resumen=f'Ofrenda {ofrenda.monto} — {ministry.nombre}',
        ministry=ministry,
        usuario=usuario,
    )
    _sincronizar_ofrenda_caja_dni(ofrenda, usuario)
    return ofrenda


@transaction.atomic
def actualizar_ofrenda(ofrenda: Ofrenda, **kwargs) -> Ofrenda:
    """Actualiza una ofrenda y sincroniza su MovimientoTesoreria vinculado si ya fue aprobada"""
    old_data = {
        'fecha': str(ofrenda.fecha),
        'monto': float(ofrenda.monto),
        'categoria': ofrenda.categoria or '',
        'clase': ofrenda.clase or '',
        'observaciones': ofrenda.observaciones or '',
    }

    for k, v in kwargs.items():
        setattr(ofrenda, k, v)
    ofrenda.save()

    HistorialLog.objects.create(
        entidad_tipo='ofrenda',
        entidad_id=ofrenda.id,
        accion='editado',
        resumen=f'Ofrenda {ofrenda.monto} — {ofrenda.ministry.nombre}',
        ministry=ofrenda.ministry,
    )

    if ofrenda.aprobado and ofrenda.movimiento_tesoreria:
        mt = ofrenda.movimiento_tesoreria
        mt.monto = ofrenda.monto
        mt.fecha = ofrenda.fecha
        mt.descripcion = f'Ofrenda {ofrenda.get_categoria_display() or ""} - {ofrenda.ministry.nombre}'.strip(' -')
        mt.save()

    _sincronizar_ofrenda_caja_dni(ofrenda)

    return ofrenda


def _sincronizar_ofrenda_caja_dni(ofrenda: Ofrenda, usuario=None):
    if ofrenda.ministry.slug != 'dni':
        return
    caja = obtener_o_crear_caja(ofrenda.ministry)
    mov, created = MovimientoCaja.objects.update_or_create(
        ofrenda_origen=ofrenda,
        defaults={
            'caja': caja,
            'tipo': 'ingreso',
            'monto': ofrenda.monto,
            'descripcion': f'Ofrenda DNI clase {ofrenda.clase or "general"}',
            'fecha': ofrenda.fecha,
            'aprobado': True,
        },
    )
    if usuario and created:
        mov.registrado_por = usuario
        mov.save(update_fields=['registrado_por'])


@transaction.atomic
def enviar_a_tesoreria(movimiento: MovimientoCaja) -> MovimientoCaja:
    """Marca un movimiento como enviado a tesorería"""
    movimiento.enviado_tesoreria = True
    movimiento.save()
    return movimiento


@transaction.atomic
def enviar_ofrenda_a_tesoreria(ofrenda: Ofrenda, usuario) -> Ofrenda:
    """Aprueba una ofrenda y la envía a tesorería"""
    ofrenda.aprobado = True
    ofrenda.envidada_tesoreria = True
    ofrenda.fecha_envio = timezone.now()
    ofrenda.save()

    mov = MovimientoTesoreria.objects.create(
        tipo='ingreso_ofrenda',
        ministry=ofrenda.ministry,
        monto=ofrenda.monto,
        fecha=ofrenda.fecha,
        descripcion=f'Ofrenda {ofrenda.get_categoria_display() or ""} - {ofrenda.ministry.nombre}'.strip(' -'),
        registrado_por=usuario,
    )

    ofrenda.movimiento_tesoreria = mov
    ofrenda.save(update_fields=['movimiento_tesoreria'])

    HistorialLog.objects.create(
        entidad_tipo='ofrenda',
        entidad_id=ofrenda.id,
        accion='editado',
        resumen=f'Aprobada: Ofrenda {ofrenda.monto} — {ofrenda.ministry.nombre}',
        ministry=ofrenda.ministry,
        usuario=usuario,
    )

    return ofrenda
