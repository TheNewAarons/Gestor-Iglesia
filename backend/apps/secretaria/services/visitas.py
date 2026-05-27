from django.db import transaction
from apps.secretaria.models import VisitaIglesia


@transaction.atomic
def registrar_visita(registrada_por, **kwargs) -> VisitaIglesia:
    return VisitaIglesia.objects.create(**kwargs)


@transaction.atomic
def actualizar_visita(visita: VisitaIglesia, **kwargs) -> VisitaIglesia:
    for field, value in kwargs.items():
        setattr(visita, field, value)
    visita.save()
    return visita


@transaction.atomic
def actualizar_seguimiento(
    visita: VisitaIglesia,
    seguimiento: str,
    responsable=None,
) -> VisitaIglesia:
    visita.seguimiento = seguimiento
    if responsable:
        visita.responsable_seguimiento = responsable
    visita.save(update_fields=['seguimiento', 'responsable_seguimiento', 'updated_at'])
    return visita


@transaction.atomic
def vincular_a_miembro(visita: VisitaIglesia, miembro) -> VisitaIglesia:
    visita.miembro_vinculado = miembro
    visita.convertido_miembro = True
    visita.seguimiento = 'integrado'
    visita.save(update_fields=['miembro_vinculado', 'convertido_miembro', 'seguimiento', 'updated_at'])
    return visita
