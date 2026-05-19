from django.db import transaction
from django.db.models import Count, Q
from ..models import Ministerio, CajaMinisterio


@transaction.atomic
def crear_ministerio(**kwargs) -> Ministerio:
    """Crea un nuevo ministerio y su caja asociada"""
    ministerio = Ministerio.objects.create(**kwargs)
    CajaMinisterio.objects.create(ministry=ministerio)
    return ministerio


@transaction.atomic
def actualizar_ministerio(ministerio: Ministerio, **kwargs) -> Ministerio:
    """Actualiza los datos de un ministerio"""
    for field, value in kwargs.items():
        setattr(ministerio, field, value)
    ministerio.save()
    return ministerio


@transaction.atomic
def desactivar_ministerio(ministerio: Ministerio) -> Ministerio:
    """Desactiva un ministerio (soft delete)"""
    ministerio.activo = False
    ministerio.save()
    return ministerio
