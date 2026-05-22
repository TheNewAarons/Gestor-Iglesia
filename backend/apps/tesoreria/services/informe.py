from django.db import transaction
from ..models import ConfiguracionFinanzas, InformeMensual
from ..selectors import flujo as flujo_selectors


@transaction.atomic
def actualizar_configuracion(*, pres_distrital_pct, pres_educacional_pct, pres_evangelismo_pct, jubilacion_monto, usuario):
    config = ConfiguracionFinanzas.obtener()
    config.pres_distrital_pct = pres_distrital_pct
    config.pres_educacional_pct = pres_educacional_pct
    config.pres_evangelismo_pct = pres_evangelismo_pct
    config.jubilacion_monto = jubilacion_monto
    config.actualizado_por = usuario
    config.save()
    return config


@transaction.atomic
def generar_informe(anio, mes, usuario):
    config = ConfiguracionFinanzas.obtener()
    saldos = flujo_selectors.saldos_ministerios()

    total_ingresos = sum(s['saldo'] for s in saldos if s['saldo'] > 0)
    total_egresos_ministerios = sum(s['total_egresos'] for s in saldos)

    saldo_total = sum(s['total_ingresos'] for s in saldos) - total_egresos_ministerios

    pct_distrital = float(config.pres_distrital_pct) / 100
    pct_educacional = float(config.pres_educacional_pct) / 100
    pct_evangelismo = float(config.pres_evangelismo_pct) / 100
    jubilacion = float(config.jubilacion_monto)

    pres_distrital = round(saldo_total * pct_distrital, 2)
    pres_educacional = round(saldo_total * pct_educacional, 2)
    pres_evangelismo = round(saldo_total * pct_evangelismo, 2)

    ministerios_principales = ['mni', 'dni', 'jni']
    principales = [s for s in saldos if s['ministry_slug'] in ministerios_principales]
    secundarios = [s for s in saldos if s['ministry_slug'] not in ministerios_principales]

    datos = {
        'ingresos': {
            'saldo_mes_pasado': {
                'otros_ministerios': float(sum(s['saldo'] for s in secundarios if s['saldo'] > 0)),
                'mni': float(next((s['saldo'] for s in principales if s['ministry_slug'] == 'mni'), 0)),
                'dni': float(next((s['saldo'] for s in principales if s['ministry_slug'] == 'dni'), 0)),
                'jni': float(next((s['saldo'] for s in principales if s['ministry_slug'] == 'jni'), 0)),
            },
            'ofrendas_totales': float(sum(s['total_ingresos'] for s in saldos)),
            'ministerios_secundarios': [
                {
                    'nombre': s['ministry_nombre'],
                    'slug': s['ministry_slug'],
                    'ingresos': s['total_ingresos'],
                }
                for s in secundarios
            ],
            'principales': {
                'mni': float(next((s['total_ingresos'] for s in principales if s['ministry_slug'] == 'mni'), 0)),
                'dni': float(next((s['total_ingresos'] for s in principales if s['ministry_slug'] == 'dni'), 0)),
                'jni': float(next((s['total_ingresos'] for s in principales if s['ministry_slug'] == 'jni'), 0)),
            },
        },
        'egresos': {
            'iglesia_local': {
                'pres_distrital': float(pres_distrital),
                'pres_educacional': float(pres_educacional),
                'pres_evangelismo': float(pres_evangelismo),
                'jubilacion': jubilacion,
            },
            'ministerios_secundarios': [
                {
                    'nombre': s['ministry_nombre'],
                    'slug': s['ministry_slug'],
                    'egresos': s['total_egresos'],
                }
                for s in secundarios
            ],
            'principales': {
                'mni': float(next((s['total_egresos'] for s in principales if s['ministry_slug'] == 'mni'), 0)),
                'dni': float(next((s['total_egresos'] for s in principales if s['ministry_slug'] == 'dni'), 0)),
                'jni': float(next((s['total_egresos'] for s in principales if s['ministry_slug'] == 'jni'), 0)),
            },
        },
        'totales': {
            'total_ingresos': float(total_ingresos),
            'total_egresos': float(total_egresos_ministerios + pres_distrital + pres_educacional + pres_evangelismo + jubilacion),
            'saldo_final': float(saldo_total - pres_distrital - pres_educacional - pres_evangelismo - jubilacion),
        },
        'configuracion': {
            'pres_distrital_pct': float(config.pres_distrital_pct),
            'pres_educacional_pct': float(config.pres_educacional_pct),
            'pres_evangelismo_pct': float(config.pres_evangelismo_pct),
            'jubilacion_monto': jubilacion,
        },
    }

    informe, _ = InformeMensual.objects.update_or_create(
        anio=anio, mes=mes,
        defaults={'datos': datos, 'generado_por': usuario}
    )
    return informe
