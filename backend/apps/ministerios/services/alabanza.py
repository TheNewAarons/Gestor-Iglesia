from django.db import transaction
from django.db.models import Q
from datetime import date
from ..models import Cancion, ProgramaAlabanza, Ministerio


@transaction.atomic
def crear_cancion(**kwargs) -> Cancion:
    """Agrega una canción al banco"""
    return Cancion.objects.create(**kwargs)


@transaction.atomic
def actualizar_cancion(cancion: Cancion, **kwargs) -> Cancion:
    """Actualiza una canción"""
    for field, value in kwargs.items():
        setattr(cancion, field, value)
    cancion.save()
    return cancion


@transaction.atomic
def generar_programa_automatico(ministry: Ministerio, fecha: date, creado_por) -> ProgramaAlabanza:
    """Genera un programa dominical automático evitando canciones recientes"""
    ultimo_programa = ProgramaAlabanza.objects.filter(
        ministry=ministry, fecha__lt=fecha
    ).order_by('-fecha').first()

    canciones_usadas = []
    if ultimo_programa:
        canciones_usadas = [a['id'] for a in ultimo_programa.alabanzas]

    programa = []
    categorias = ['rapida', 'rapida', 'media', 'lenta', 'lenta']

    for cat in categorias:
        disponibles = Cancion.objects.filter(categoria=cat).exclude(id__in=canciones_usadas)
        if disponibles.exists():
            cancion = disponibles.first()
        else:
            disponibles = Cancion.objects.filter(categoria=cat)
            cancion = disponibles.order_by('?').first() if disponibles.exists() else None

        if cancion:
            programa.append({
                'id': cancion.id,
                'titulo': cancion.titulo,
                'categoria': cancion.categoria,
                'tono': cancion.tono
            })
            canciones_usadas.append(cancion.id)

    return ProgramaAlabanza.objects.create(
        ministry=ministry, fecha=fecha, alabanzas=programa, creado_por=creado_por
    )
