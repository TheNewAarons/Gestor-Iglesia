from django.db.models import Q
from apps.secretaria.models import VisitaIglesia


def listar_visitas(activo=True, seguimiento=None, search=None, fecha_desde=None, fecha_hasta=None):
    qs = VisitaIglesia.objects.select_related(
        'ministerio_interes', 'responsable_seguimiento', 'miembro_vinculado'
    )
    if activo is not None:
        qs = qs.filter(activo=activo)
    if seguimiento:
        qs = qs.filter(seguimiento=seguimiento)
    if search:
        qs = qs.filter(
            Q(nombre__icontains=search) |
            Q(telefono__icontains=search) |
            Q(email__icontains=search)
        )
    if fecha_desde:
        qs = qs.filter(fecha_primera_visita__gte=fecha_desde)
    if fecha_hasta:
        qs = qs.filter(fecha_primera_visita__lte=fecha_hasta)
    return qs


def visitantes_activos():
    return VisitaIglesia.objects.filter(
        activo=True,
        seguimiento='sin_seguimiento',
    ).select_related('ministerio_interes')
