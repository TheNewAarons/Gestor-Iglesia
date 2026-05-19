from django.db import transaction
from ..models import CajaMinisterio, MovimientoCaja, Ofrenda


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
    return movimiento


@transaction.atomic
def crear_ofrenda(ministry, **kwargs) -> Ofrenda:
    """Registra una ofrenda"""
    ofrenda = Ofrenda.objects.create(ministry=ministry, **kwargs)
    return ofrenda


@transaction.atomic
def enviar_a_tesoreria(movimiento: MovimientoCaja) -> MovimientoCaja:
    """Marca un movimiento como enviado a tesorería"""
    movimiento.enviado_tesoreria = True
    movimiento.save()
    return movimiento


@transaction.atomic
def enviar_ofrenda_a_tesoreria(ofrenda: Ofrenda) -> Ofrenda:
    """Marca una ofrenda como enviada a tesorería"""
    ofrenda.envidada_tesoreria = True
    ofrenda.save()
    return ofrenda
