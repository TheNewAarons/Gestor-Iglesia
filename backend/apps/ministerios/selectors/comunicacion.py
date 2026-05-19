from ..models import RecursoComunicacion, IdeaComunicacion, Ministerio


def listar_recursos(filters: dict = None):
    """Lista recursos de comunicación con filtros"""
    queryset = RecursoComunicacion.objects.select_related('ministry')
    if filters:
        if ministry_slug := filters.get('ministerio'):
            queryset = queryset.filter(ministry__slug=ministry_slug)
        if tipo := filters.get('tipo'):
            queryset = queryset.filter(tipo=tipo)
    return queryset


def listar_ideas(filters: dict = None):
    """Lista ideas de comunicación con filtros"""
    queryset = IdeaComunicacion.objects.select_related('ministry')
    if filters:
        if ministry_slug := filters.get('ministerio'):
            queryset = queryset.filter(ministry__slug=ministry_slug)
        if completada := filters.get('completada'):
            queryset = queryset.filter(completada=completada.lower() == 'true')
    return queryset
