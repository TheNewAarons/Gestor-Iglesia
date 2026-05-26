from django.core.management.base import BaseCommand
from apps.ministerios.models import EnfoqueMNI


ENFOQUES = [
    (1, 'Ofrenda Especial Génesis', 'Enfoque del mes de enero'),
    (2, 'Ofrenda de Alabastro', 'Enfoque del mes de febrero'),
    (3, 'Movilización "El Llamado"', 'Enfoque del mes de marzo'),
    (4, 'Movilización "Oportunidades para Servir"', 'Enfoque del mes de abril'),
    (5, 'Cuenta la Historia', 'Enfoque del mes de mayo'),
    (6, 'Jóvenes y Niños', 'Enfoque del mes de junio'),
    (7, 'Movilización "La Iglesia Enviando"', 'Enfoque del mes de julio'),
    (8, 'Ofrenda de Alabastro', 'Enfoque del mes de agosto'),
    (9, 'Eslabones', 'Enfoque del mes de septiembre'),
    (10, 'La Iglesia Perseguida', 'Enfoque del mes de octubre'),
    (11, 'FEM', 'Enfoque del mes de noviembre'),
    (12, 'Ofrenda de Acción de Gracias', 'Enfoque del mes de diciembre'),
]


class Command(BaseCommand):
    help = 'Crea los 12 enfoques mensuales del MNI'

    def handle(self, *args, **options):
        creado = 0
        actualizado = 0

        for mes, titulo, descripcion in ENFOQUES:
            enf, created = EnfoqueMNI.objects.update_or_create(
                mes=mes,
                defaults={'titulo': titulo, 'descripcion': descripcion},
            )
            if created:
                creado += 1
            else:
                actualizado += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Enfoques MNI: {creado} creados, {actualizado} actualizados'
            )
        )
