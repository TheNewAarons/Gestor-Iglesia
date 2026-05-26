from django.db import transaction
from django.db.models import Sum
from ..models import ConfiguracionFinanzas, InformeMensual, MovimientoTesoreria, CuotaFija
from ..selectors import flujo as flujo_selectors
from apps.ministerios.models import MovimientoCaja, Ofrenda


@transaction.atomic
def actualizar_configuracion(*, pres_distrital_pct=None, pres_educacional_pct=None, pres_evangelismo_pct=None, jubilacion_monto=None, usuario):
    config = ConfiguracionFinanzas.obtener()
    if pres_distrital_pct is not None:
        config.pres_distrital_pct = pres_distrital_pct
    if pres_educacional_pct is not None:
        config.pres_educacional_pct = pres_educacional_pct
    if pres_evangelismo_pct is not None:
        config.pres_evangelismo_pct = pres_evangelismo_pct
    if jubilacion_monto is not None:
        config.jubilacion_monto = jubilacion_monto
    config.actualizado_por = usuario
    config.save()
    return config


@transaction.atomic
def generar_informe(anio, mes, usuario):
    config = ConfiguracionFinanzas.obtener()
    pct_distrital = float(config.pres_distrital_pct) / 100
    pct_educacional = float(config.pres_educacional_pct) / 100
    pct_evangelismo = float(config.pres_evangelismo_pct) / 100
    jubilacion = float(config.jubilacion_monto)

    principales_slugs = ['mni', 'dni', 'jni']
    secundarios_slugs = [
        'mam', 'vid', 'explo', 'danza', 'teatro', 'alabanza',
        'comunicaciones', 'compasion', 'nazakids', 'adulto-mayor'
    ]

    # --- Cuotas fijas ---
    cuotas = {c.ministry.slug: {} for c in CuotaFija.objects.select_related('ministry').all()}
    for c in CuotaFija.objects.select_related('ministry').all():
        slug = c.ministry.slug
        cuotas[slug][c.tipo] = float(c.monto)

    def get_cuota(slug, tipo):
        return cuotas.get(slug, {}).get(tipo, 0)

    # --- Movimientos de caja por ministry ---
    movs_mes = MovimientoCaja.objects.filter(fecha__year=anio, fecha__month=mes, aprobado=True)
    ingresos_caja = {}
    egresos_caja = {}
    for m in movs_mes.select_related('caja__ministry'):
        slug = m.caja.ministry.slug
        if slug not in ingresos_caja:
            ingresos_caja[slug] = 0
            egresos_caja[slug] = 0
        val = float(m.monto)
        if m.tipo == 'ingreso':
            ingresos_caja[slug] += val
        else:
            egresos_caja[slug] += val

    # --- Ofrendas por ministry ---
    ofrendas_mes = Ofrenda.objects.filter(fecha__year=anio, fecha__month=mes, aprobado=True)
    ofrendas_ministry = {}
    for o in ofrendas_mes:
        slug = o.ministry.slug
        ofrendas_ministry[slug] = ofrendas_ministry.get(slug, 0) + float(o.monto)

    # --- Movimientos directos de tesoreria ---
    tes_movs = MovimientoTesoreria.objects.filter(fecha__year=anio, fecha__month=mes)
    tes_por_tipo = {}
    for t in tes_movs:
        tes_por_tipo[t.tipo] = tes_por_tipo.get(t.tipo, 0) + float(t.monto)

    def ti(key):
        return tes_por_tipo.get(key, 0)

    # ======= INGRESOS =======
    # 1. Saldo del mes pasado
    informe_ant = flujo_selectors.obtener_informe_mes_anterior(anio, mes)
    if informe_ant:
        saldo_final_ant = informe_ant.datos.get('totales', {}).get('saldo_final', 0)
    else:
        saldo_final_ant = 0

    def ingresos_secundario(slug):
        return ingresos_caja.get(slug, 0) + ofrendas_ministry.get(slug, 0)

    # 2. Iglesia local
    total_ofrendas = sum(ofrendas_ministry.values())
    total_diezmos = ti('ingreso_diezmo')
    total_especiales = ti('ingreso_especial')

    # 3. Otros ministerios
    ingresos_secundarios = {}
    for slug in secundarios_slugs:
        ingresos_secundarios[slug] = ingresos_secundario(slug)

    # 4. DNI
    ingresos_dni = ingresos_caja.get('dni', 0) + ofrendas_ministry.get('dni', 0)

    # 5. JNI
    ingresos_jni = ingresos_caja.get('jni', 0) + ofrendas_ministry.get('jni', 0)

    # 6. MNI
    mni_ofrendas = flujo_selectors.ofrendas_por_categoria_mni(mes, anio)
    ingresos_mni = ingresos_caja.get('mni', 0) + mni_ofrendas['total']

    # 7. Total entradas
    total_ingresos_mes = (
        total_ofrendas + total_diezmos + total_especiales +
        sum(ingresos_secundarios.values()) +
        ingresos_dni + ingresos_jni + ingresos_mni
    )

    # ======= EGRESOS =======
    # 1. Iglesia local
    sosten_pastoral = ti('egreso_sosten_pastoral')
    beneficios_pastorales = ti('egreso_beneficios_pastorales')
    varios_iglesia = ti('egreso_varios_iglesia')
    fondo_contingencia = ti('egreso_fondo_contingencia')

    saldo_base_pres = saldo_final_ant + total_ingresos_mes
    pres_distrital = round(saldo_base_pres * pct_distrital, 2)
    pres_educacional = round(saldo_base_pres * pct_educacional, 2)
    pres_evangelismo = round(saldo_base_pres * pct_evangelismo, 2)

    coce_mni = get_cuota('mni', 'coce')
    coce_dni = get_cuota('dni', 'coce')
    coce_jni = get_cuota('jni', 'coce')
    coce_total = coce_mni + coce_dni + coce_jni

    # 2. Egresos secundarios
    egresos_secundarios = {}
    for slug in secundarios_slugs:
        egresos_secundarios[slug] = egresos_caja.get(slug, 0)

    # 3. DNI
    cuota_distrital_dni = get_cuota('dni', 'cuota_distrital')
    egresos_dni = egresos_caja.get('dni', 0)

    # 4. JNI
    cuota_distrital_jni = get_cuota('jni', 'cuota_distrital')
    egresos_jni = egresos_caja.get('jni', 0)

    # 5. MNI
    cuota_distrital_mni = get_cuota('mni', 'cuota_distrital')
    egresos_mni = egresos_caja.get('mni', 0)
    fem_egreso = mni_ofrendas['fem']

    # 6. Total gastos
    total_egresos_mes = (
        sosten_pastoral + beneficios_pastorales + varios_iglesia +
        fondo_contingencia + pres_distrital + pres_educacional +
        pres_evangelismo + jubilacion + coce_total +
        sum(egresos_secundarios.values()) +
        egresos_dni + cuota_distrital_dni + coce_dni +
        egresos_jni + cuota_distrital_jni + coce_jni +
        egresos_mni + cuota_distrital_mni + coce_mni +
        mni_ofrendas['caja_alabastro'] + fem_egreso
    )

    # Saldo final
    saldo_final = saldo_final_ant + total_ingresos_mes - total_egresos_mes

    datos = {
        'ingresos': {
            'saldo_mes_pasado': {
                'otros_ministerios': float(sum(ingresos_secundarios.values())),
                'iglesia': float(saldo_final_ant - sum(ingresos_secundarios.values())),
                'dni': float(saldo_final_ant * 0.1 if informe_ant else 0),
                'jni': float(saldo_final_ant * 0.1 if informe_ant else 0),
                'mni': float(saldo_final_ant * 0.1 if informe_ant else 0),
                'total': float(saldo_final_ant),
            },
            'iglesia_local': {
                'ofrendas': float(total_ofrendas),
                'diezmos': float(total_diezmos),
                'especiales': float(total_especiales),
            },
            'otros_ministerios': [
                {'nombre': s.replace('-', ' ').title(), 'slug': s, 'ingresos': v}
                for s, v in ingresos_secundarios.items()
            ],
            'fondos_especiales': {
                'ahorro': float(ti('ingreso_ahorro')),
                'proyectos': float(ti('ingreso_proyectos')),
            },
            'dni': {'total_ofrendas': float(ingresos_dni)},
            'jni': {'total_ofrendas': float(ingresos_jni)},
            'mni': {
                'ofrenda_general': mni_ofrendas['ofrenda_general'],
                'caja_alabastro': mni_ofrendas['caja_alabastro'],
                'accion_gracias': mni_ofrendas['accion_gracias'],
                'dip': mni_ofrendas['dip'],
                'oracion_ayuno': mni_ofrendas['oracion_ayuno'],
                'fem': mni_ofrendas['fem'],
                'otros': mni_ofrendas['otros'],
                'total': mni_ofrendas['total'],
            },
            'total_entradas_anio': float(total_ingresos_mes),
        },
        'egresos': {
            'iglesia_local': {
                'sosten_pastoral': float(sosten_pastoral),
                'beneficios_pastorales': float(beneficios_pastorales),
                'varios_iglesia': float(varios_iglesia),
                'pres_distrital': float(pres_distrital),
                'pres_educacional': float(pres_educacional),
                'pres_evangelismo': float(pres_evangelismo),
                'jubilacion': float(jubilacion),
                'coce': float(coce_total),
                'fondo_contingencia': float(fondo_contingencia),
            },
            'otros_ministerios': [
                {'nombre': s.replace('-', ' ').title(), 'slug': s, 'egresos': v}
                for s, v in egresos_secundarios.items()
            ],
            'dni': {
                'gastos_locales': float(egresos_dni),
                'cuota_distrital': float(cuota_distrital_dni),
                'coce': float(coce_dni),
            },
            'jni': {
                'gastos_locales': float(egresos_jni),
                'cuota_distrital': float(cuota_distrital_jni),
                'coce': float(coce_jni),
            },
            'mni': {
                'gastos_locales': float(egresos_mni),
                'cuota_distrital': float(cuota_distrital_mni),
                'coce': float(coce_mni),
                'caja_alabastro': mni_ofrendas['caja_alabastro'],
                'fem': fem_egreso,
            },
            'total_gastos': float(total_egresos_mes),
        },
        'totales': {
            'saldo_mes_pasado': float(saldo_final_ant),
            'total_ingresos': float(total_ingresos_mes),
            'total_gastos': float(total_egresos_mes),
            'saldo_final': float(saldo_final),
        },
        'configuracion': {
            'pres_distrital_pct': float(config.pres_distrital_pct),
            'pres_educacional_pct': float(config.pres_educacional_pct),
            'pres_evangelismo_pct': float(config.pres_evangelismo_pct),
            'jubilacion_monto': float(config.jubilacion_monto),
        },
    }

    informe, _ = InformeMensual.objects.update_or_create(
        anio=anio, mes=mes,
        defaults={'datos': datos, 'generado_por': usuario}
    )
    return informe
