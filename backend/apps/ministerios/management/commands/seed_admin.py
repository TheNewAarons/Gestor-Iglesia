from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Crea un usuario administrador por defecto'

    def handle(self, *args, **options):
        username = 'admin'
        password = 'admin123'
        email = 'admin@iglesia.com'
        first_name = 'Administrador'
        last_name = 'Sistema'

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f'El usuario "{username}" ya existe'))
            return

        User.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_staff=True,
            is_superuser=True,
            rol='admin'
        )

        self.stdout.write(
            self.style.SUCCESS(f'Usuario creado: {username} / {password}')
        )
