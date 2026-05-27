from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta


def resumen_membresia() -> dict:
    from apps.ministerios.models import Miembro, Ministerio

    total = Miembro.objects.filter(activo=True).count()
    total_inactivos = Miembro.objects.filter(activo=False).count()

    por_clase = list(
        Miembro.objects.filter(activo=True)
        .values('clase')
        .annotate(cantidad=Count('id'))
        .order_by('clase')
    )

    por_ministerio = list(
        Ministerio.objects.annotate(
            miembros_activos=Count('miembros', filter=Q(miembros__activo=True))
        ).values('nombre', 'miembros_activos').order_by('-miembros_activos')
    )

    hace_30_dias = timezone.now().date() - timedelta(days=30)
    nuevos_mes = Miembro.objects.filter(
        activo=True,
        fecha_ingreso__gte=hace_30_dias,
    ).count()

    return {
        'total_activos': total,
        'total_inactivos': total_inactivos,
        'nuevos_ultimo_mes': nuevos_mes,
        'por_clase': por_clase,
        'por_ministerio': por_ministerio,
    }


def resumen_secretaria() -> dict:
    from apps.secretaria.models import (
        ActaReunion, SolicitudTramite, VisitaIglesia, ComunicadoInterno
    )

    hoy = timezone.now().date()
    inicio_mes = hoy.replace(day=1)

    return {
        'actas_mes': ActaReunion.objects.filter(fecha_reunion__gte=inicio_mes).count(),
        'actas_pendientes': ActaReunion.objects.filter(estado='borrador').count(),
        'solicitudes_pendientes': SolicitudTramite.objects.filter(estado='pendiente').count(),
        'visitantes_sin_seguimiento': VisitaIglesia.objects.filter(
            activo=True, seguimiento='sin_seguimiento'
        ).count(),
        'comunicados_publicados': ComunicadoInterno.objects.filter(publicado=True).count(),
    }
