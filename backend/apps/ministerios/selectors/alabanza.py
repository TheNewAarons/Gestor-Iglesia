from django.db.models import Q
from ..models import Cancion, ProgramaAlabanza, Ministerio


def listar_canciones(categoria: str = None, search: str = None):
    """Lista canciones del banco con filtros por categoría y búsqueda textual."""
    queryset = Cancion.objects.all()
    if categoria:
        queryset = queryset.filter(categoria=categoria)
    if search:
        queryset = queryset.filter(
            Q(titulo__icontains=search) | Q(artista__icontains=search)
        )
    return queryset.order_by('titulo')


def obtener_cancion(pk: int):
    """Obtiene una canción por ID"""
    try:
        return Cancion.objects.get(pk=pk)
    except Cancion.DoesNotExist:
        return None


def listar_programas(ministry_slug: str = None):
    """Lista programas de alabanza con filtro opcional por ministerio"""
    queryset = ProgramaAlabanza.objects.select_related('ministry', 'creado_por')
    if ministry_slug:
        queryset = queryset.filter(ministry__slug=ministry_slug)
    return queryset


def obtener_programa(pk: int):
    """Obtiene un programa por ID"""
    try:
        return ProgramaAlabanza.objects.select_related('ministry', 'creado_por').get(pk=pk)
    except ProgramaAlabanza.DoesNotExist:
        return None
