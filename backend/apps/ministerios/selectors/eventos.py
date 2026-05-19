from django.db.models import Q
from ..models import Evento, PlanificacionActividad, Ministerio


def listar_eventos(filters: dict = None):
    """Lista eventos con filtros"""
    queryset = Evento.objects.select_related('ministry', 'creado_por').prefetch_related('ministerios_relacionados')

    if filters:
        if ministry_slug := filters.get('ministerio'):
            queryset = queryset.filter(
                Q(ministry__slug=ministry_slug) |
                Q(ministerios_relacionados__slug=ministry_slug)
            ).distinct()
        if fecha_inicio := filters.get('fecha_inicio'):
            queryset = queryset.filter(fecha_inicio__gte=fecha_inicio)
        if fecha_fin := filters.get('fecha_fin'):
            queryset = queryset.filter(fecha_inicio__lte=fecha_fin)
        if tipo := filters.get('tipo'):
            queryset = queryset.filter(tipo=tipo)

    return queryset


def listar_eventos_por_ministerio(ministry: Ministerio):
    """Eventos de un ministerio específico"""
    return ministry.eventos.select_related('creado_por').prefetch_related('ministerios_relacionados').all()


def listar_planificaciones(ministry: Ministerio, filters: dict = None):
    """Lista planificaciones de un ministerio"""
    queryset = ministry.planificaciones.select_related('responsable')
    if filters:
        if estado := filters.get('estado'):
            queryset = queryset.filter(estado=estado)
    return queryset
