from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore

_scheduler = BackgroundScheduler(timezone='America/Asuncion')
_started = False


def _envio_dominical_job():
    from apps.secretaria.services.whatsapp import ejecutar_envio_dominical
    ejecutar_envio_dominical(force=False)


def _archivar_comunicados_vencidos():
    from datetime import date
    from apps.secretaria.models import ComunicadoInterno
    vencidos = ComunicadoInterno.objects.filter(
        publicado=True,
        fecha_vencimiento__lt=date.today()
    )
    count = vencidos.update(publicado=False)
    if count > 0:
        print(f'[Secretaría] Archivados {count} comunicados vencidos.')


def _informe_mensual_job():
    from apps.tesoreria.tasks import generar_informe_mensual_automatico
    generar_informe_mensual_automatico()


def _cumpleanos_job():
    from apps.tesoreria.tasks import notificar_cumpleanos_hoy
    notificar_cumpleanos_hoy()


def _pendientes_job():
    from apps.tesoreria.tasks import alertar_pendientes_vencidos
    alertar_pendientes_vencidos()


def _backup_job():
    from apps.secretaria.backup import realizar_backup
    realizar_backup()


def start():
    global _started
    if _started:
        return
    _started = True

    _scheduler.add_jobstore(DjangoJobStore(), 'default')
    _scheduler.add_job(
        _envio_dominical_job,
        trigger=CronTrigger(day_of_week='sun', hour=9, minute=0),
        id='envio_dominical_whatsapp',
        replace_existing=True,
        misfire_grace_time=3600,
    )
    _scheduler.add_job(
        _archivar_comunicados_vencidos,
        trigger=CronTrigger(hour=0, minute=30),
        id='archivar_comunicados_vencidos',
        replace_existing=True,
        misfire_grace_time=3600,
    )
    _scheduler.add_job(
        _informe_mensual_job,
        trigger=CronTrigger(day=1, hour=8, minute=0),
        id='informe_mensual_auto',
        replace_existing=True,
        misfire_grace_time=7200,
    )
    _scheduler.add_job(
        _cumpleanos_job,
        trigger=CronTrigger(hour=8, minute=30),
        id='cumpleanos_diario',
        replace_existing=True,
        misfire_grace_time=3600,
    )
    _scheduler.add_job(
        _pendientes_job,
        trigger=CronTrigger(day_of_week='mon', hour=9, minute=0),
        id='pendientes_alerta',
        replace_existing=True,
        misfire_grace_time=3600,
    )
    _scheduler.add_job(
        _backup_job,
        trigger=CronTrigger(hour=2, minute=0),
        id='backup_diario',
        replace_existing=True,
        misfire_grace_time=7200,
    )
    _scheduler.start()
