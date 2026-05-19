from ..models import Inventario, Ministerio


def listar_inventario(ministry: Ministerio, filters: dict = None):
    """Lista el inventario de un ministerio con filtros"""
    queryset = ministry.inventario.all()
    if filters:
        if categoria := filters.get('categoria'):
            queryset = queryset.filter(categoria=categoria)
        if estado := filters.get('estado'):
            queryset = queryset.filter(estado=estado)
    return queryset


def obtener_item_inventario(pk: int):
    """Obtiene un item de inventario por ID"""
    try:
        return Inventario.objects.select_related('ministry').get(pk=pk)
    except Inventario.DoesNotExist:
        return None
