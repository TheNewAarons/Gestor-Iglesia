from django.core.management.base import BaseCommand
from apps.ministerios.models import Ministerio


MINISTERIOS = [
    {'nombre': 'MNI', 'slug': 'mni', 'descripcion': 'Ministerio de Nuevos Integrantes', 'color': '#10B981', 'icono': 'user-plus'},
    {'nombre': 'DNI', 'slug': 'dni', 'descripcion': 'Discipulado Nuevo Instituto', 'color': '#3B82F6', 'icono': 'book-open'},
    {'nombre': 'JNI', 'slug': 'jni', 'descripcion': 'Juventud Nueva Israel', 'color': '#8B5CF6', 'icono': 'users'},
    {'nombre': 'MAM', 'slug': 'mam', 'descripcion': 'Ministerio de Animación y Ministère', 'color': '#EC4899', 'icono': 'heart'},
    {'nombre': 'VID', 'slug': 'vid', 'descripcion': 'Visitas a Dios', 'color': '#F59E0B', 'icono': 'home'},
    {'nombre': 'EXPLO', 'slug': 'explo', 'descripcion': 'Escuela de Predicadores y Líderes', 'color': '#EF4444', 'icono': 'graduation-cap'},
    {'nombre': 'Danza', 'slug': 'danza', 'descripcion': 'Ministerio de Danza', 'color': '#14B8A6', 'icono': 'music'},
    {'nombre': 'Teatro', 'slug': 'teatro', 'descripcion': 'Ministerio de Teatro', 'color': '#6366F1', 'icono': 'theater-masks'},
    {'nombre': 'Alabanza', 'slug': 'alabanza', 'descripcion': 'Ministerio de Alabanza', 'color': '#F97316', 'icono': 'microphone'},
    {'nombre': 'Comunicaciones', 'slug': 'comunicaciones', 'descripcion': 'Ministerio de Comunicaciones', 'color': '#06B6D4', 'icono': 'broadcast'},
    {'nombre': 'Compasión', 'slug': 'compasion', 'descripcion': 'Ministerio de Compasión', 'color': '#84CC16', 'icono': 'hand-holding-heart'},
    {'nombre': 'NazaKids', 'slug': 'nazakids', 'descripcion': 'Ministerio de Niños', 'color': '#FBBF24', 'icono': 'child'},
    {'nombre': 'Adulto Mayor', 'slug': 'adulto-mayor', 'descripcion': 'Ministerio de Adulto Mayor', 'color': '#78716C', 'icono': 'users'},
]


class Command(BaseCommand):
    help = 'Crea los 13 ministerios por defecto'

    def handle(self, *args, **options):
        creado = 0
        actualizado = 0

        for m in MINISTERIOS:
            ministry, created = Ministerio.objects.update_or_create(
                slug=m['slug'],
                defaults={
                    'nombre': m['nombre'],
                    'descripcion': m['descripcion'],
                    'color': m['color'],
                    'icono': m['icono'],
                    'activo': True
                }
            )

            if created:
                creado += 1
            else:
                actualizado += 1

        self.stdout.write(
            self.style.SUCCESS(f'Se crearon {creado} ministerios y se actualizaron {actualizado}')
        )