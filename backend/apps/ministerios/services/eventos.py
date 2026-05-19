from django.db import transaction
from ..models import Evento, PlanificacionActividad


@transaction.atomic
def crear_evento(ministry, creado_por, ministerios_relacionados=None, **kwargs) -> Evento:
    """Crea un evento del calendario"""
    evento = Evento.objects.create(ministry=ministry, creado_por=creado_por, **kwargs)
    if ministerios_relacionados:
        evento.ministerios_relacionados.set(ministerios_relacionados)
    return evento


@transaction.atomic
def actualizar_evento(evento: Evento, ministerios_relacionados=None, **kwargs) -> Evento:
    """Actualiza un evento"""
    for field, value in kwargs.items():
        setattr(evento, field, value)
    evento.save()
    if ministerios_relacionados is not None:
        evento.ministerios_relacionados.set(ministerios_relacionados)
    return evento


@transaction.atomic
def crear_planificacion(ministry, responsable, ministerios_relacionados=None, **kwargs) -> PlanificacionActividad:
    """Crea una planificación de actividad"""
    plan = PlanificacionActividad.objects.create(
        ministry=ministry, responsable=responsable, **kwargs
    )
    if ministerios_relacionados:
        plan.ministerios_relacionados.set(ministerios_relacionados)
    return plan


@transaction.atomic
def actualizar_planificacion(plan: PlanificacionActividad, ministerios_relacionados=None, **kwargs) -> PlanificacionActividad:
    """Actualiza una planificación"""
    for field, value in kwargs.items():
        setattr(plan, field, value)
    plan.save()
    if ministerios_relacionados is not None:
        plan.ministerios_relacionados.set(ministerios_relacionados)
    return plan
