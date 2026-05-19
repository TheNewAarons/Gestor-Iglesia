import pytest
from django.contrib.auth import get_user_model
from apps.ministerios.models import Ministerio, Miembro, CajaMinisterio
from apps.ministerios.selectors import ministerio as ministerio_selectors
from apps.ministerios.selectors import miembro as miembro_selectors
from apps.ministerios.selectors import usuarios as usuarios_selectors
from apps.ministerios.services import ministerio as ministerio_services
from apps.ministerios.services import usuarios as usuarios_services

User = get_user_model()


@pytest.mark.django_db
class TestAuth:
    """Pruebas de autenticación JWT"""

    def test_login_success(self, api_client, admin_user):
        response = api_client.post('/api/v1/auth/login/', {
            'username': 'admin_test',
            'password': 'admin123',
        }, format='json')

        assert response.status_code == 200
        assert response.data['success'] is True
        assert response.data['user']['username'] == 'admin_test'
        assert response.cookies.get('access_token') is not None
        assert response.cookies.get('refresh_token') is not None

    def test_login_invalid_credentials(self, api_client):
        response = api_client.post('/api/v1/auth/login/', {
            'username': 'noexiste',
            'password': 'mal123',
        }, format='json')

        assert response.status_code == 401

    def test_me_authenticated(self, authenticated_client, admin_user):
        response = authenticated_client.get('/api/v1/auth/me/')
        assert response.status_code == 200
        assert response.data['username'] == 'admin_test'
        assert response.data['rol'] == 'admin'

    def test_me_unauthenticated(self, api_client):
        response = api_client.get('/api/v1/auth/me/')
        assert response.status_code == 401

    def test_logout(self, authenticated_client):
        response = authenticated_client.post('/api/v1/auth/logout/')
        assert response.status_code == 200
        # Las cookies deben ser eliminadas
        assert response.cookies.get('access_token')
        assert response.cookies.get('refresh_token')


@pytest.mark.django_db
class TestMinisterios:
    """Pruebas de ministerios"""

    def test_list_ministerios(self, api_client, ministry):
        response = api_client.get('/api/v1/ministerios/')
        assert response.status_code == 200
        assert len(response.data['results']) >= 1

    def test_retrieve_ministerio(self, api_client, ministry):
        response = api_client.get(f'/api/v1/ministerios/{ministry.slug}/')
        assert response.status_code == 200
        assert response.data['nombre'] == 'MNI'

    def test_create_ministerio_admin(self, authenticated_client):
        response = authenticated_client.post('/api/v1/ministerios/', {
            'nombre': 'Danza',
            'slug': 'danza',
            'color': '#14B8A6',
            'icono': 'music',
        }, format='json')
        assert response.status_code == 201
        assert response.data['nombre'] == 'Danza'

    def test_dashboard(self, api_client, ministry):
        response = api_client.get(f'/api/v1/ministerios/{ministry.slug}/dashboard/')
        assert response.status_code == 200
        assert 'ministerio' in response.data
        assert 'miembros_count' in response.data


@pytest.mark.django_db
class TestMiembros:
    """Pruebas de miembros"""

    def test_list_miembros(self, api_client, ministry, miembro):
        response = api_client.get('/api/v1/miembros/')
        assert response.status_code == 200
        assert len(response.data['results']) >= 1

    def test_create_miembro_admin(self, authenticated_client, ministry):
        response = authenticated_client.post('/api/v1/miembros/', {
            'ministry': ministry.id,
            'primer_nombre': 'María',
            'primer_apellido': 'García',
            'rol_en_ministerio': 'miembro',
        }, format='json')
        assert response.status_code == 201
        assert response.data['nombre_completo'] == 'María García'


@pytest.mark.django_db
class TestUsuarios:
    """Pruebas de gestión de usuarios"""

    def test_list_usuarios_admin(self, authenticated_client, admin_user):
        response = authenticated_client.get('/api/v1/usuarios/')
        assert response.status_code == 200
        assert len(response.data) >= 1

    def test_list_usuarios_sin_permiso(self, api_client, lider_user):
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(lider_user)
        api_client.cookies['access_token'] = str(refresh.access_token)

        response = api_client.get('/api/v1/usuarios/')
        assert response.status_code == 403

    def test_cambiar_rol(self, authenticated_client, lider_user):
        response = authenticated_client.post(
            f'/api/v1/usuarios/{lider_user.id}/cambiar-rol/',
            {'rol': 'secretaria'},
            format='json'
        )
        assert response.status_code == 200
        assert response.data['rol'] == 'secretaria'


@pytest.mark.django_db
class TestSelectors:
    """Pruebas de la capa selectors"""

    def test_listar_ministerios(self, ministry):
        ministerios = ministerio_selectors.listar_ministerios()
        assert ministerios.count() >= 1

    def test_obtener_por_slug(self, ministry):
        result = ministerio_selectors.obtener_ministerio_por_slug('mni')
        assert result is not None
        assert result.nombre == 'MNI'

    def test_obtener_por_slug_inexistente(self):
        result = ministerio_selectors.obtener_ministerio_por_slug('noexiste')
        assert result is None

    def test_listar_miembros(self, ministry, miembro):
        miembros = miembro_selectors.listar_miembros()
        assert miembros.count() >= 1

    def test_listar_usuarios(self, admin_user):
        usuarios = usuarios_selectors.listar_usuarios()
        assert usuarios.count() >= 1


@pytest.mark.django_db
class TestServices:
    """Pruebas de la capa services"""

    def test_crear_usuario(self, admin_user):
        user = usuarios_services.crear_usuario(
            creado_por=admin_user,
            username='nuevo_user',
            password='pass123',
            first_name='Nuevo',
            last_name='Usuario',
            email='nuevo@test.com',
            rol='concilio',
        )
        assert user.username == 'nuevo_user'
        assert user.rol == 'concilio'
        assert user.creado_por == admin_user

    def test_cambiar_rol_usuario(self, lider_user):
        user = usuarios_services.cambiar_rol_usuario(lider_user, 'tesorera')
        assert user.rol == 'tesorera'

    def test_desactivar_usuario(self, lider_user):
        user = usuarios_services.desactivar_usuario(lider_user)
        assert user.is_active is False

    def test_crear_ministerio_with_caja(self):
        ministry = ministerio_services.crear_ministerio(
            nombre='Test Ministry',
            slug='test-ministry',
        )
        assert ministry.nombre == 'Test Ministry'
        assert hasattr(ministry, 'caja')
