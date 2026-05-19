from django.db import transaction
from ..models import Inventario


@transaction.atomic
def crear_item_inventario(ministry, **kwargs) -> Inventario:
    """Crea un item de inventario para un ministerio"""
    item = Inventario.objects.create(ministry=ministry, **kwargs)
    return item


@transaction.atomic
def actualizar_item_inventario(item: Inventario, **kwargs) -> Inventario:
    """Actualiza un item de inventario"""
    for field, value in kwargs.items():
        setattr(item, field, value)
    item.save()
    return item


@transaction.atomic
def eliminar_item_inventario(item: Inventario):
    """Elimina un item de inventario"""
    item.delete()
