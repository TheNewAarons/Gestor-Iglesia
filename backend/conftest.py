import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin_user(db):
    user = User.objects.create_user(
        username='admin_test',
        password='admin123',
        email='admin@test.com',
        first_name='Admin',
        last_name='Test',
        rol='admin',
        is_staff=True,
        is_superuser=True,
    )
    return user


@pytest.fixture
def authenticated_client(api_client, admin_user):
    from rest_framework_simplejwt.tokens import RefreshToken

    refresh = RefreshToken.for_user(admin_user)
    api_client.cookies['access_token'] = str(refresh.access_token)
    api_client.cookies['refresh_token'] = str(refresh)
    return api_client


@pytest.fixture
def lider_user(db):
    user = User.objects.create_user(
        username='lider_test',
        password='lider123',
        email='lider@test.com',
        first_name='Líder',
        last_name='Test',
        rol='lider_ministerio',
    )
    return user


@pytest.fixture
def concilio_user(db):
    user = User.objects.create_user(
        username='concilio_test',
        password='concilio123',
        email='concilio@test.com',
        first_name='Concilio',
        last_name='Test',
        rol='concilio',
    )
    return user


@pytest.fixture
def ministry(db):
    from apps.ministerios.models import Ministerio
    return Ministerio.objects.create(
        nombre='MNI',
        slug='mni',
        descripcion='Ministerio de Nuevos Integrantes',
        color='#10B981',
        icono='user-plus',
    )


@pytest.fixture
def ministry_with_leader(db, ministry, lider_user):
    lider_user.ministerios_lidera.add(ministry)
    return ministry


@pytest.fixture
def miembro(db, ministry):
    from apps.ministerios.models import Miembro
    return Miembro.objects.create(
        ministry=ministry,
        primer_nombre='Juan',
        primer_apellido='Pérez',
        telefono='0991123456',
        email='juan@test.com',
        rol_en_ministerio='miembro',
    )
