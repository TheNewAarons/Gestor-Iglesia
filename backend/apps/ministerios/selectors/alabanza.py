from ..models import Cancion, ProgramaAlabanza, Ministerio


def listar_canciones(categoria: str = None):
    """Lista canciones del banco con filtro opcional por categoría"""
    queryset = Cancion.objects.all()
    if categoria:
        queryset = queryset.filter(categoria=categoria)
    return queryset


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
