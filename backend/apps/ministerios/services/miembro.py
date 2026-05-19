from django.db import transaction
from ..models import Miembro


@transaction.atomic
def crear_miembro(ministry, **kwargs) -> Miembro:
    """Crea un nuevo miembro en un ministerio"""
    miembro = Miembro.objects.create(ministry=ministry, **kwargs)
    return miembro


@transaction.atomic
def actualizar_miembro(miembro: Miembro, **kwargs) -> Miembro:
    """Actualiza los datos de un miembro"""
    for field, value in kwargs.items():
        setattr(miembro, field, value)
    miembro.save()
    return miembro


@transaction.atomic
def desactivar_miembro(miembro: Miembro) -> Miembro:
    """Desactiva un miembro (soft delete)"""
    miembro.activo = False
    miembro.save()
    return miembro
