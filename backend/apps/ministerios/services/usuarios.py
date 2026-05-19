from django.db import transaction
from django.contrib.auth import get_user_model
from ..models import Ministerio

User = get_user_model()


@transaction.atomic
def crear_usuario(creado_por, ministerios_lidera=None, **kwargs) -> User:
    """Crea un nuevo usuario con rol y permisos"""
    ministerios_ids = kwargs.pop('ministerios_lidera_ids', [])
    user = User.objects.create_user(creado_por=creado_por, **kwargs)

    if not ministerios_ids and ministerios_lidera:
        ministerios_ids = ministerios_lidera
    if ministerios_ids:
        ministerios = Ministerio.objects.filter(id__in=ministerios_ids)
        user.ministerios_lidera.set(ministerios)

    return user


@transaction.atomic
def actualizar_usuario(user: User, **kwargs) -> User:
    """Actualiza datos y rol de un usuario"""
    ministerios_ids = kwargs.pop('ministerios_lidera_ids', None)
    nueva_password = kwargs.pop('password_nueva', None)

    for field, value in kwargs.items():
        if hasattr(user, field):
            setattr(user, field, value)

    user.save()

    if ministerios_ids is not None:
        ministerios = Ministerio.objects.filter(id__in=ministerios_ids)
        user.ministerios_lidera.set(ministerios)

    if nueva_password:
        user.set_password(nueva_password)
        user.save()

    return user


@transaction.atomic
def desactivar_usuario(user: User) -> User:
    """Desactiva un usuario (soft delete)"""
    user.is_active = False
    user.save()
    return user


@transaction.atomic
def cambiar_rol_usuario(user: User, nuevo_rol: str) -> User:
    """Cambia el rol de un usuario"""
    user.rol = nuevo_rol
    user.save()
    return user


@transaction.atomic
def asignar_ministerios_usuario(user: User, ministerios_ids: list[int]) -> User:
    """Asigna los ministerios que lidera un usuario"""
    ministerios = Ministerio.objects.filter(id__in=ministerios_ids)
    user.ministerios_lidera.set(ministerios)
    user.save()
    return user
