from apps.secretaria.models import ActaReunion


def listar_actas(estado=None, tipo=None):
    qs = ActaReunion.objects.select_related('creado_por', 'aprobada_por')
    if estado:
        qs = qs.filter(estado=estado)
    if tipo:
        qs = qs.filter(tipo=tipo)
    return qs


def obtener_acta(pk: int) -> ActaReunion:
    return ActaReunion.objects.select_related('creado_por', 'aprobada_por').get(pk=pk)
