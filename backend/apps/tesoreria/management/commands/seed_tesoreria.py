from django.core.management.base import BaseCommand
from apps.tesoreria.models import ConfiguracionFinanzas


class Command(BaseCommand):
    help = 'Crear configuración por defecto de tesorería'

    def handle(self, *args, **options):
        config = ConfiguracionFinanzas.obtener()
        self.stdout.write(self.style.SUCCESS(
            f'Configuración de finanzas creada: '
            f'PRES.DISTRITAL={config.pres_distrital_pct}%, '
            f'PRES.EDUCACIONAL={config.pres_educacional_pct}%, '
            f'PRES.EVANGELISMO={config.pres_evangelismo_pct}%, '
            f'Jubilación={config.jubilacion_monto}'
        ))
