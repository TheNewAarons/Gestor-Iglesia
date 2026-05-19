from django.db import transaction
from ..models import RecursoComunicacion, IdeaComunicacion


@transaction.atomic
def crear_recurso(ministry, **kwargs) -> RecursoComunicacion:
    """Crea un recurso de comunicación"""
    return RecursoComunicacion.objects.create(ministry=ministry, **kwargs)


@transaction.atomic
def actualizar_recurso(recurso: RecursoComunicacion, **kwargs) -> RecursoComunicacion:
    """Actualiza un recurso de comunicación"""
    for field, value in kwargs.items():
        setattr(recurso, field, value)
    recurso.save()
    return recurso


@transaction.atomic
def crear_idea(ministry, **kwargs) -> IdeaComunicacion:
    """Crea una idea de comunicación"""
    return IdeaComunicacion.objects.create(ministry=ministry, **kwargs)


@transaction.atomic
def actualizar_idea(idea: IdeaComunicacion, **kwargs) -> IdeaComunicacion:
    """Actualiza una idea de comunicación"""
    for field, value in kwargs.items():
        setattr(idea, field, value)
    idea.save()
    return idea


@transaction.atomic
def marcar_idea_completada(idea: IdeaComunicacion) -> IdeaComunicacion:
    """Marca una idea como completada"""
    from django.utils import timezone
    idea.completada = True
    idea.fecha_completada = timezone.now()
    idea.save()
    return idea
