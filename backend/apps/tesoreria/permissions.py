from rest_framework import permissions


class IsTesoreraOrAdmin(permissions.BasePermission):
    """Permite acceso a tesorera, admin y pastora."""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.rol in ['admin', 'tesorera', 'pastora']


class IsAdmin(permissions.BasePermission):
    """Solo admin puede acceder (para configuración)."""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.rol == 'admin'
