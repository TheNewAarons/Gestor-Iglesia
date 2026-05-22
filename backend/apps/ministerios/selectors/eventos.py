from datetime import date

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


def listar_eventos_calendario(year: int, month: int, ministerio_slug: str = None):
    """Eventos del mes para la vista de calendario, incluyendo multi-día"""
    import calendar
    last_day = calendar.monthrange(year, month)[1]
    month_start = date(year, month, 1)
    month_end = date(year, month, last_day)

    queryset = Evento.objects.select_related('ministry', 'creado_por').prefetch_related('ministerios_relacionados')
    queryset = queryset.filter(
        Q(fecha_inicio__year=year, fecha_inicio__month=month) |
        Q(fecha_fin__year=year, fecha_fin__month=month) |
        Q(fecha_inicio__lte=month_end, fecha_fin__gte=month_start)
    )

    if ministerio_slug:
        queryset = queryset.filter(
            Q(ministry__slug=ministerio_slug) |
            Q(ministerios_relacionados__slug=ministerio_slug)
        ).distinct()

    return queryset.order_by('fecha_inicio')


def listar_eventos_por_ministerio(ministry: Ministerio):
    """Eventos de un ministerio específico, incluyendo compartidos"""
    return Evento.objects.filter(
        Q(ministry=ministry) | Q(ministerios_relacionados=ministry)
    ).select_related('ministry', 'creado_por').prefetch_related('ministerios_relacionados').distinct().order_by('fecha_inicio')


def listar_planificaciones(ministry: Ministerio, filters: dict = None):
    """Lista planificaciones de un ministerio"""
    queryset = ministry.planificaciones.select_related('responsable')
    if filters:
        if estado := filters.get('estado'):
            queryset = queryset.filter(estado=estado)
    return queryset
