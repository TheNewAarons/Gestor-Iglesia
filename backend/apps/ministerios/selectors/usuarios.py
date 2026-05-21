from django.contrib.auth import get_user_model
from django.db.models import Q
from ..models import Ministerio, Permiso

User = get_user_model()


def listar_usuarios():
    """Lista todos los usuarios con datos relacionados"""
    return User.objects.select_related('creado_por').prefetch_related(
        'ministerios_lidera'
    ).order_by('-date_joined')


def listar_usuarios_simples(search=None):
    """Lista usuarios con datos básicos para vinculación"""
    qs = User.objects.filter(is_active=True)
    if search:
        qs = qs.filter(
            Q(username__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
    return qs.values('id', 'username', 'first_name', 'last_name', 'email', 'telefono', 'rol')[:50]


def obtener_usuario(pk: int):
    """Obtiene un usuario por ID"""
    try:
        return User.objects.select_related('creado_por').prefetch_related(
            'ministerios_lidera'
        ).get(pk=pk)
    except User.DoesNotExist:
        return None


def obtener_usuario_por_username(username: str):
    """Obtiene un usuario por username"""
    try:
        return User.objects.get(username=username)
    except User.DoesNotExist:
        return None


def listar_roles():
    """Lista los roles disponibles con su display"""
    return [{'value': r[0], 'label': r[1]} for r in User.ROLES]


def listar_ministerios_para_asignacion():
    """Lista ministerios activos para asignación a lideres"""
    return Ministerio.objects.filter(activo=True).values('id', 'nombre', 'slug')


def listar_permisos():
    """Lista todos los permisos configurados"""
    return Permiso.objects.all()
