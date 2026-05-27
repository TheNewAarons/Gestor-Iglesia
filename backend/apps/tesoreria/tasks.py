from datetime import date, timedelta
import logging

logger = logging.getLogger(__name__)


def generar_informe_mensual_automatico():
    """Job día 1 de cada mes: genera informe del mes anterior."""
    from .services.informe import generar_informe
    from .models import InformeMensual

    hoy = date.today()
    mes_anterior = (hoy.replace(day=1) - timedelta(days=1))
    anio, mes = mes_anterior.year, mes_anterior.month

    if InformeMensual.objects.filter(anio=anio, mes=mes).exists():
        logger.info('Informe %s/%s ya existe, omitiendo generación automática.', mes, anio)
        return

    try:
        informe = generar_informe(anio=anio, mes=mes, usuario=None)
        logger.info('Informe mensual %s/%s generado automáticamente (id=%s).', mes, anio, informe.pk)
    except Exception as exc:
        logger.error('Error generando informe mensual automático %s/%s: %s', mes, anio, exc)


def notificar_cumpleanos_hoy():
    """Job diario 8:30am: envía WhatsApp con cumpleaños del día."""
    from apps.ministerios.models import Miembro
    from apps.secretaria.models import ConfiguracionWhatsApp
    from apps.secretaria.services.whatsapp import enviar_mensaje

    hoy = date.today()
    miembros_hoy = list(
        Miembro.objects.filter(
            activo=True,
            fecha_nacimiento__month=hoy.month,
            fecha_nacimiento__day=hoy.day,
        ).select_related('ministry')
    )

    if not miembros_hoy:
        return

    config = ConfiguracionWhatsApp.obtener()
    if not config.grupo_jid or not config.activo:
        return

    nombres = '\n'.join(
        f'🎂 {m.nombre_completo} ({m.ministry.nombre if m.ministry else "sin ministerio"})'
        for m in miembros_hoy
    )
    texto = f'*¡Feliz Cumpleaños!* 🎉\n\nHoy cumplen años:\n{nombres}\n\n¡Que Dios los bendiga!'

    try:
        enviar_mensaje(config.grupo_jid, texto)
        logger.info('Notificación cumpleaños enviada: %d miembro(s).', len(miembros_hoy))
    except Exception as exc:
        logger.error('Error enviando notificación cumpleaños: %s', exc)


def alertar_pendientes_vencidos():
    """Job lunes 9am: alerta si hay ofrendas/movimientos sin aprobar > 7 días."""
    from apps.ministerios.models import MovimientoCaja, Ofrenda
    from apps.secretaria.models import ConfiguracionWhatsApp
    from apps.secretaria.services.whatsapp import enviar_mensaje

    umbral = date.today() - timedelta(days=7)

    ofrendas = MovimientoCaja.objects.filter(aprobado=False, fecha__date__lt=umbral).count() \
        if hasattr(MovimientoCaja, 'fecha') else 0
    movimientos = Ofrenda.objects.filter(aprobado=False, fecha__lt=umbral).count()

    total = ofrendas + movimientos
    if total == 0:
        return

    config = ConfiguracionWhatsApp.obtener()
    if not config.grupo_jid or not config.activo:
        return

    texto = (
        f'⚠️ *Pendientes sin aprobar*\n\n'
        f'Hay {total} item(s) con más de 7 días sin aprobar:\n'
        f'• Movimientos de caja: {ofrendas}\n'
        f'• Ofrendas: {movimientos}\n\n'
        f'Ingresá al sistema para revisarlos.'
    )

    try:
        enviar_mensaje(config.grupo_jid, texto)
        logger.info('Alerta pendientes enviada: %d item(s) vencidos.', total)
    except Exception as exc:
        logger.error('Error enviando alerta pendientes: %s', exc)
