from rest_framework import permissions
from django.contrib.auth import get_user_model

User = get_user_model()


class IsAdminOrReadOnly(permissions.BasePermission):
    """Solo admin puede modificar, todos pueden ver"""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.rol == 'admin'


class IsLiderOrAdmin(permissions.BasePermission):
    """Líder de ministry o Admin pueden acceder"""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.user.rol in ['admin', 'pastora']:
            return True

        if view.kwargs.get('slug'):
            ministry = view.kwargs.get('slug')
            return request.user.ministerios_lidera.filter(slug=ministry).exists()

        return False


class IsTesoreraOrAdmin(permissions.BasePermission):
    """Solo tesorera y admin pueden acceder a finanzas"""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.rol in ['admin', 'tesorera', 'pastora']


class IsSecretariaOrAdmin(permissions.BasePermission):
    """Solo secretaria y admin pueden acceder a membresía"""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.rol in ['admin', 'secretaria', 'pastora']


class CanAccessMinisterio(permissions.BasePermission):
    """Verifica si el usuario tiene acceso al ministry"""
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        if request.user.rol in ['admin', 'pastora']:
            return True

        if request.user.rol == 'lider_ministerio':
            if hasattr(obj, 'ministry'):
                return obj.ministry in request.user.ministerios_lidera.all()
            return obj in request.user.ministerios_lidera.all()

        if request.user.rol in ['concilio']:
            return True

        return False


class IsAdmin(permissions.BasePermission):
    """Solo admin global puede acceder"""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.rol == 'admin'


class CanManageUsers(permissions.BasePermission):
    """Admin puede gestionar usuarios"""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.rol == 'admin'


class CanManageUsersOrSelf(permissions.BasePermission):
    """Admin o propio usuario pueden acceder"""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.user.rol == 'admin':
            return True

        if view.kwargs.get('pk'):
            try:
                user_obj = User.objects.get(pk=view.kwargs.get('pk'))
                return user_obj == request.user
            except User.DoesNotExist:
                return False

        return True
