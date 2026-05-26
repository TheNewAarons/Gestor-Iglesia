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
        for clase_val in ['parvulos', 'principiantes', 'primarios', 'jovenes', 'adultos']:
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
                           clase: str = None, nombre: str = None,
                           fecha_inicio: str = None, fecha_fin: str = None,
                           presente: bool = None):
    """Asistencia acumulativa por persona con filtros"""
    queryset = ministry.asistencias.all()

    if fecha_inicio and fecha_fin:
        queryset = queryset.filter(fecha__gte=fecha_inicio, fecha__lte=fecha_fin)
    else:
        if not mes:
            mes = date.today().month
        if not anio:
            anio = date.today().year
        queryset = queryset.filter(fecha__month=mes, fecha__year=anio)

    if presente is not None:
        queryset = queryset.filter(presente=presente)

    if clase:
        queryset = queryset.filter(clase=clase)

    miembros_ids = queryset.values_list('miembro', flat=True).distinct()

    resultados = []
    for miembro_id in miembros_ids:
        if miembro_id is None:
            continue
        try:
            miembro = Miembro.objects.get(id=miembro_id)
            if nombre and nombre.lower() not in miembro.nombre_completo.lower():
                continue
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
    clases = ['parvulos', 'principiantes', 'primarios', 'jovenes', 'adultos']

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


def biblias_por_clase(ministry: Ministerio, mes: int = None, anio: int = None):
    if not mes:
        mes = date.today().month
    if not anio:
        anio = date.today().year

    queryset = ministry.asistencias.filter(
        fecha__month=mes, fecha__year=anio, tiene_biblia=True
    )
    clases = ['parvulos', 'principiantes', 'primarios', 'jovenes', 'adultos']

    resultados = []
    total = 0
    for clase_val in clases:
        count = queryset.filter(clase=clase_val).count()
        total += count
        resultados.append({'clase': clase_val, 'biblias': count})

    return {'por_clase': resultados, 'total_general': total}


def visitas_por_periodo(ministry: Ministerio, fecha_inicio: str = None, fecha_fin: str = None):
    """Visitas totales por período"""
    queryset = ministry.asistencias.filter(es_visita=True)
    if fecha_inicio:
        queryset = queryset.filter(fecha__gte=fecha_inicio)
    if fecha_fin:
        queryset = queryset.filter(fecha__lte=fecha_fin)
    visitas = queryset.values('nombre_visita', 'clase', 'fecha').distinct().order_by('-fecha')
    return {
        'total': queryset.values('nombre_visita').distinct().count(),
        'visitas': list(visitas)
    }


def visitas_acumuladas_por_mes(ministry: Ministerio, anio: int = None):
    """Visitas acumuladas cada mes del año"""
    if not anio:
        anio = date.today().year
    from django.db.models import Count
    queryset = ministry.asistencias.filter(es_visita=True, fecha__year=anio)
    acumulados = queryset.values('fecha__month').annotate(
        total=Count('nombre_visita', distinct=True)
    ).order_by('fecha__month')
    resultado = {m: 0 for m in range(1, 13)}
    for item in acumulados:
        resultado[item['fecha__month']] = item['total']
    return {'anio': anio, 'acumulado_por_mes': [{'mes': k, 'visitas': v} for k, v in resultado.items()]}
