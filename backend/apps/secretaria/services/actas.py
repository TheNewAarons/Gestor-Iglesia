from django.db import transaction
from django.utils import timezone
from apps.secretaria.models import ActaReunion


@transaction.atomic
def crear_acta(usuario, **kwargs) -> ActaReunion:
    return ActaReunion.objects.create(creado_por=usuario, **kwargs)


@transaction.atomic
def actualizar_acta(acta: ActaReunion, **kwargs) -> ActaReunion:
    for field, value in kwargs.items():
        setattr(acta, field, value)
    acta.save()
    return acta


@transaction.atomic
def aprobar_acta(acta: ActaReunion, aprobada_por) -> ActaReunion:
    acta.estado = 'aprobada'
    acta.aprobada_por = aprobada_por
    acta.aprobada_en = timezone.now()
    acta.save(update_fields=['estado', 'aprobada_por', 'aprobada_en', 'updated_at'])
    return acta


@transaction.atomic
def archivar_acta(acta: ActaReunion) -> ActaReunion:
    acta.estado = 'archivada'
    acta.save(update_fields=['estado', 'updated_at'])
    return acta
