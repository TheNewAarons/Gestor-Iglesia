from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """Solo admin puede modificar, todos pueden ver"""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_staff or request.user.perfil.rol == 'admin'


class IsLiderOrAdmin(permissions.BasePermission):
    """Líder de ministry o Admin pueden acceder"""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        perfil = getattr(request.user, 'perfil', None)
        if not perfil:
            return False

        if perfil.rol in ['admin', 'pastora']:
            return True

        if view.kwargs.get('slug'):
            ministry = view.kwargs.get('slug')
            return perfil.ministerios_lidera.filter(slug=ministry).exists()

        return False


class IsTesoreraOrAdmin(permissions.BasePermission):
    """Solo tesorera y admin pueden acceder a finanzas"""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        perfil = getattr(request.user, 'perfil', None)
        if not perfil:
            return False

        return perfil.rol in ['admin', 'tesorera', 'pastora']


class IsSecretariaOrAdmin(permissions.BasePermission):
    """Solo secretaria y admin pueden acceder a membresía"""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        perfil = getattr(request.user, 'perfil', None)
        if not perfil:
            return False

        return perfil.rol in ['admin', 'secretaria', 'pastora']


class CanAccessMinisterio(permissions.BasePermission):
    """Verifica si el usuario tiene acceso al ministry"""
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        perfil = getattr(request.user, 'perfil', None)
        if not perfil:
            return False

        if perfil.rol in ['admin', 'pastora']:
            return True

        if perfil.rol == 'lider_ministerio':
            if hasattr(obj, 'ministry'):
                return obj.ministry in perfil.ministerios_lidera.all()
            return obj in perfil.ministerios_lidera.all()

        if perfil.rol in ['concilio']:
            return True

        return False


class IsAdmin(permissions.BasePermission):
    """Solo admin global puede acceder"""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        perfil = getattr(request.user, 'perfil', None)
        return perfil and perfil.rol == 'admin'


class CanManageUsers(permissions.BasePermission):
    """Admin puede gestionar usuarios"""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        perfil = getattr(request.user, 'perfil', None)
        return perfil and perfil.rol == 'admin'


class CanManageUsersOrSelf(permissions.BasePermission):
    """Admin o propio usuario pueden acceder"""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        perfil = getattr(request.user, 'perfil', None)
        if not perfil:
            return False

        if perfil.rol == 'admin':
            return True

        if view.kwargs.get('pk'):
            try:
                from .models import PerfilUsuario
                perfil_obj = PerfilUsuario.objects.get(pk=view.kwargs.get('pk'))
                return perfil_obj.user == request.user
            except PerfilUsuario.DoesNotExist:
                return False

        return True