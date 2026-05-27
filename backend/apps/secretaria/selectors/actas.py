from django.db.models import Q
from apps.secretaria.models import ActaReunion


def listar_actas(estado=None, tipo=None, search=None, fecha_desde=None, fecha_hasta=None):
    qs = ActaReunion.objects.select_related('creado_por', 'aprobada_por')
    if estado:
        qs = qs.filter(estado=estado)
    if tipo:
        qs = qs.filter(tipo=tipo)
    if search:
        qs = qs.filter(
            Q(titulo__icontains=search) |
            Q(presidida_por__icontains=search) |
            Q(lugar__icontains=search)
        )
    if fecha_desde:
        qs = qs.filter(fecha_reunion__gte=fecha_desde)
    if fecha_hasta:
        qs = qs.filter(fecha_reunion__lte=fecha_hasta)
    return qs


def obtener_acta(pk: int) -> ActaReunion:
    return ActaReunion.objects.select_related('creado_por', 'aprobada_por').get(pk=pk)
