from django.db.models import Q
from apps.secretaria.models import SolicitudTramite


def listar_solicitudes(estado=None, tipo=None, prioridad=None, search=None, fecha_desde=None, fecha_hasta=None):
    qs = SolicitudTramite.objects.select_related(
        'solicitante_miembro', 'ministerio', 'registrada_por', 'atendida_por'
    )
    if estado:
        qs = qs.filter(estado=estado)
    if tipo:
        qs = qs.filter(tipo=tipo)
    if prioridad:
        qs = qs.filter(prioridad=prioridad)
    if search:
        qs = qs.filter(
            Q(solicitante_nombre__icontains=search) |
            Q(descripcion__icontains=search)
        )
    if fecha_desde:
        qs = qs.filter(fecha_solicitud__gte=fecha_desde)
    if fecha_hasta:
        qs = qs.filter(fecha_solicitud__lte=fecha_hasta)
    return qs


def obtener_solicitud(pk: int) -> SolicitudTramite:
    return SolicitudTramite.objects.select_related(
        'solicitante_miembro', 'ministerio', 'registrada_por', 'atendida_por'
    ).get(pk=pk)
