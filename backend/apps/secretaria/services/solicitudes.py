import os
from django.db import transaction
from django.utils import timezone
from apps.secretaria.models import SolicitudTramite
from apps.secretaria.services.documentos import (
    generar_carta_membresia,
    generar_carta_recomendacion,
)


@transaction.atomic
def crear_solicitud(registrada_por, **kwargs) -> SolicitudTramite:
    return SolicitudTramite.objects.create(registrada_por=registrada_por, **kwargs)


@transaction.atomic
def actualizar_estado_solicitud(
    solicitud: SolicitudTramite,
    estado: str,
    usuario,
    notas: str = '',
) -> SolicitudTramite:
    solicitud.estado = estado
    solicitud.atendida_por = usuario
    if notas:
        solicitud.resolucion_notas = notas
    if estado in ('aprobada', 'rechazada'):
        solicitud.fecha_resolucion = timezone.now().date()
    solicitud.save()
    return solicitud


@transaction.atomic
def generar_documento_solicitud(solicitud: SolicitudTramite) -> SolicitudTramite:
    miembro = solicitud.solicitante_miembro
    if not miembro:
        return solicitud

    if solicitud.tipo == 'carta_membresia':
        pdf_bytes = generar_carta_membresia(miembro)
    elif solicitud.tipo == 'carta_recomendacion':
        iglesia_destino = solicitud.datos_adicionales.get('iglesia_destino', '')
        pdf_bytes = generar_carta_recomendacion(miembro, iglesia_destino)
    else:
        return solicitud

    from django.core.files.base import ContentFile
    filename = f"solicitud_{solicitud.id}_{solicitud.tipo}.pdf"
    solicitud.documento_generado.save(filename, ContentFile(pdf_bytes), save=True)
    return solicitud
