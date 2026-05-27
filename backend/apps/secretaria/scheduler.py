from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore

_scheduler = BackgroundScheduler(timezone='America/Asuncion')
_started = False


def _envio_dominical_job():
    from apps.secretaria.services.whatsapp import ejecutar_envio_dominical
    ejecutar_envio_dominical(force=False)


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
    _scheduler.start()
