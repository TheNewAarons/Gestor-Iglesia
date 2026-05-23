from django.db import transaction
from apps.ministerios.models import MovimientoCaja, CajaMinisterio


@transaction.atomic
def registrar_traspaso(*, ministry_slug, monto, descripcion, usuario):
    """Registra un traspaso: crea un egreso en la caja del ministry y lo marca como enviado a tesoreria."""
    caja = CajaMinisterio.objects.select_related('ministry').get(ministry__slug=ministry_slug)
    movimiento = MovimientoCaja.objects.create(
        caja=caja,
        tipo='egreso',
        monto=monto,
        descripcion=descripcion or f'Traspaso a tesoreria - {caja.ministry.nombre}',
        registrado_por=usuario,
        enviado_tesoreria=True,
    )
    return movimiento
