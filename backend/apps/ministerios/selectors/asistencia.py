from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from datetime import date, timedelta
from ..models import Asistencia, Miembro, Ministerio


def listar_asistencias(ministry: Ministerio, filters: dict = None):
    """Lista asistencias de un ministerio con filtros"""
    queryset = ministry.asistencias.select_related('miembro')

    if filters:
        if fecha := filters.get('fecha'):
            queryset = queryset.filter(fecha=fecha)
        elif 'semana_actual' in filters:
            queryset = queryset.filter(fecha__gte=date.today() - timedelta(days=7))
            del filters['semana_actual']
        if clase := filters.get('clase'):
            queryset = queryset.filter(clase=clase)

    return queryset


def resumen_asistencia(ministry: Ministerio, mes: int = None, anio: int = None):
    """Resumen de asistencia por día en un mes"""
    if not mes:
        mes = date.today().month
    if not anio:
        anio = date.today().year

    queryset = ministry.asistencias.filter(
        fecha__month=mes, fecha__year=anio
    )

    fechas_unicas = queryset.values('fecha').distinct().order_by('fecha')

    resultados = []
    for item in fechas_unicas:
        fecha = item['fecha']
        registros = queryset.filter(fecha=fecha)

        por_clase = {}
        for clase_val in ['ninos', 'jovenes', 'adultos_jovenes', 'adultos', 'adultos_mayores']:
            count = registros.filter(clase=clase_val).count()
            if count > 0:
                por_clase[clase_val] = count

        ofrendas_dia = ministry.ofrendas.filter(fecha=fecha).aggregate(total=Sum('monto'))['total'] or 0

        resultados.append({
            'fecha': fecha.strftime('%Y-%m-%d'),
            'total_asistencia': registros.filter(presente=True).count(),
            'total_visitas': registros.filter(es_visita=True).count(),
            'total_biblias': registros.filter(tiene_biblia=True).count(),
            'total_ofrendas': float(ofrendas_dia),
            'por_clase': por_clase
        })

    return resultados


def asistencia_acumulativa(ministry: Ministerio, mes: int = None, anio: int = None,
                           clase: str = None):
    """Asistencia acumulativa por persona en un mes"""
    if not mes:
        mes = date.today().month
    if not anio:
        anio = date.today().year

    queryset = ministry.asistencias.filter(
        fecha__month=mes, fecha__year=anio, presente=True
    )

    if clase:
        queryset = queryset.filter(clase=clase)

    miembros_ids = queryset.values_list('miembro', flat=True).distinct()

    resultados = []
    for miembro_id in miembros_ids:
        if miembro_id is None:
            continue
        try:
            miembro = Miembro.objects.get(id=miembro_id)
            count = queryset.filter(miembro=miembro_id).count()
            resultados.append({
                'miembro_id': miembro.id,
                'nombre_completo': miembro.nombre_completo,
                'clase': miembro.clase,
                'asistencias_count': count
            })
        except Miembro.DoesNotExist:
            continue

    visitas_count = queryset.filter(es_visita=True).values('nombre_visita').distinct().count()

    return {
        'miembros': sorted(resultados, key=lambda x: x['asistencias_count'], reverse=True),
        'visitas_total': visitas_count,
        'total_asistencias': sum(r['asistencias_count'] for r in resultados)
    }


def estadisticas_asistencia(ministry: Ministerio, mes: int = None, anio: int = None):
    """Estadísticas de asistencia por clase para un mes"""
    if not mes:
        mes = date.today().month
    if not anio:
        anio = date.today().year

    queryset = ministry.asistencias.filter(fecha__month=mes, fecha__year=anio)
    miembros = ministry.miembros.filter(activo=True)
    clases = ['ninos', 'jovenes', 'adultos_jovenes', 'adultos', 'adultos_mayores']

    estadisticas = {}
    for clase_val in clases:
        clase_query = queryset.filter(clase=clase_val)
        estadisticas[clase_val] = {
            'miembros_registrados': miembros.filter(clase=clase_val).count(),
            'asistencias_totales': clase_query.filter(presente=True).count(),
            'visitas': clase_query.filter(es_visita=True).count(),
            'biblias': clase_query.filter(tiene_biblia=True).count()
        }

    return estadisticas
