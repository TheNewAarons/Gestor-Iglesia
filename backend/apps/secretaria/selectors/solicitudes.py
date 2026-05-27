from apps.secretaria.models import SolicitudTramite


def listar_solicitudes(estado=None, tipo=None, prioridad=None):
    qs = SolicitudTramite.objects.select_related(
        'solicitante_miembro', 'ministerio', 'registrada_por', 'atendida_por'
    )
    if estado:
        qs = qs.filter(estado=estado)
    if tipo:
        qs = qs.filter(tipo=tipo)
    if prioridad:
        qs = qs.filter(prioridad=prioridad)
    return qs


def obtener_solicitud(pk: int) -> SolicitudTramite:
    return SolicitudTramite.objects.select_related(
        'solicitante_miembro', 'ministerio', 'registrada_por', 'atendida_por'
    ).get(pk=pk)
