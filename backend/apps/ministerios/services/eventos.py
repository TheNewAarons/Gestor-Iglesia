from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import transaction

from ..models import Evento, PlanificacionActividad


def validar_conflicto_horario(ubicacion, fecha_inicio, fecha_fin=None, exclude_id=None):
    """Valida que no haya otro evento en la misma ubicación con solapamiento de horario.
    Retorna una lista de eventos conflictivos (vacía si no hay conflicto)."""
    if not ubicacion or not fecha_inicio:
        return []

    end_time = fecha_fin if fecha_fin else fecha_inicio + timedelta(hours=1)

    candidatos = Evento.objects.filter(
        ubicacion__iexact=ubicacion,
        fecha_inicio__lt=end_time,
        fecha_inicio__gte=fecha_inicio - timedelta(days=1),
    )

    if exclude_id:
        candidatos = candidatos.exclude(id=exclude_id)

    conflictos = []
    for evento in candidatos:
        existing_end = evento.fecha_fin if evento.fecha_fin else evento.fecha_inicio + timedelta(hours=1)
        if existing_end > fecha_inicio:
            conflictos.append(evento)

    return conflictos


@transaction.atomic
def crear_evento(ministry, creado_por, ministerios_relacionados=None, forzar=False, **kwargs) -> Evento:
    """Crea un evento del calendario"""
    ubicacion = kwargs.get('ubicacion', '')
    fecha_inicio = kwargs.get('fecha_inicio')
    fecha_fin = kwargs.get('fecha_fin')

    if ubicacion and fecha_inicio and not forzar:
        conflictos = validar_conflicto_horario(ubicacion, fecha_inicio, fecha_fin)
        if conflictos:
            raise ValidationError({
                'tipo': 'conflicto_horario',
                'mensaje': f'Ya existe un evento en "{ubicacion}" en ese horario.',
                'conflictos': [
                    {'id': e.id, 'titulo': e.titulo, 'fecha_inicio': e.fecha_inicio.isoformat()}
                    for e in conflictos
                ]
            })

    evento = Evento.objects.create(ministry=ministry, creado_por=creado_por, **kwargs)
    if ministerios_relacionados:
        evento.ministerios_relacionados.set(ministerios_relacionados)
    return evento


@transaction.atomic
def actualizar_evento(evento: Evento, ministerios_relacionados=None, forzar=False, **kwargs) -> Evento:
    """Actualiza un evento"""
    ubicacion = kwargs.get('ubicacion', evento.ubicacion)
    fecha_inicio = kwargs.get('fecha_inicio', evento.fecha_inicio)
    fecha_fin = kwargs.get('fecha_fin', evento.fecha_fin)

    if ubicacion and fecha_inicio and not forzar:
        conflictos = validar_conflicto_horario(ubicacion, fecha_inicio, fecha_fin, exclude_id=evento.id)
        if conflictos:
            raise ValidationError({
                'tipo': 'conflicto_horario',
                'mensaje': f'Ya existe un evento en "{ubicacion}" en ese horario.',
                'conflictos': [
                    {'id': e.id, 'titulo': e.titulo, 'fecha_inicio': e.fecha_inicio.isoformat()}
                    for e in conflictos
                ]
            })

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
