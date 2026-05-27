from apps.secretaria.models import VisitaIglesia


def listar_visitas(activo=True, seguimiento=None):
    qs = VisitaIglesia.objects.select_related(
        'ministerio_interes', 'responsable_seguimiento', 'miembro_vinculado'
    )
    if activo is not None:
        qs = qs.filter(activo=activo)
    if seguimiento:
        qs = qs.filter(seguimiento=seguimiento)
    return qs


def visitantes_activos():
    return VisitaIglesia.objects.filter(
        activo=True,
        seguimiento='sin_seguimiento',
    ).select_related('ministerio_interes')
