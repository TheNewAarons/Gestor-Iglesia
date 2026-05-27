from django.db import transaction
from django.contrib.auth import get_user_model
from ..models import Ministerio, Miembro

User = get_user_model()


def _validar_asignacion_ministerios(user, ministerios_ids, rol=None):
    rol = rol or user.rol

    if not ministerios_ids:
        return

    ministerios = Ministerio.objects.filter(id__in=ministerios_ids)

    if rol == 'lider_ministerio':
        if len(ministerios_ids) > 1:
            raise ValueError('Un líder solo puede liderar un ministerio')

        for m in ministerios:
            lider_actual = User.objects.filter(
                rol='lider_ministerio',
                ministerios_lidera=m,
                is_active=True,
            ).exclude(pk=user.pk if user.pk else None).first()
            if lider_actual:
                raise ValueError(
                    f'El ministerio "{m.nombre}" ya tiene un líder asignado'
                )


def _sincronizar_miembros(user, ministerios_nuevos):
    if ministerios_nuevos is None:
        return

    old_ids = set(user.ministerios_lidera.values_list('id', flat=True))
    new_ids = set(ministerios_nuevos)

    agregar = new_ids - old_ids
    remover = old_ids - new_ids

    rol_en_ministerio = 'lider' if user.rol == 'lider_ministerio' else 'miembro'

    for ministry_id in agregar:
        Miembro.objects.update_or_create(
            ministry_id=ministry_id,
            usuario=user,
            defaults={
                'primer_nombre': user.first_name or user.username,
                'primer_apellido': user.last_name or '',
                'email': user.email or '',
                'telefono': user.telefono or '',
                'rol_en_ministerio': rol_en_ministerio,
                'origen': 'sistema',
                'activo': True,
            }
        )

    for ministry_id in remover:
        Miembro.objects.filter(
            ministry_id=ministry_id,
            usuario=user,
            origen='sistema',
        ).delete()


@transaction.atomic
def crear_usuario(creado_por, ministerios_lidera=None, **kwargs) -> User:
    """Crea un nuevo usuario con rol y permisos"""
    ministerios_ids = kwargs.pop('ministerios_lidera_ids', [])
    rol = kwargs.get('rol', User._meta.get_field('rol').default)

    user = User.objects.create_user(creado_por=creado_por, **kwargs)

    if not ministerios_ids and ministerios_lidera:
        ministerios_ids = ministerios_lidera

    if ministerios_ids:
        _validar_asignacion_ministerios(user, ministerios_ids, rol=rol)
        _sincronizar_miembros(user, ministerios_ids)
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
        _validar_asignacion_ministerios(user, ministerios_ids, rol=user.rol)
        _sincronizar_miembros(user, ministerios_ids)
        ministerios = Ministerio.objects.filter(id__in=ministerios_ids)
        user.ministerios_lidera.set(ministerios)

    if nueva_password:
        user.set_password(nueva_password)
        user.save()

    return user


@transaction.atomic
def desactivar_usuario(user: User) -> User:
    """Desactiva un usuario: soft delete + limpieza de ministerios + invalidar JWT."""
    user.is_active = False
    user.ministerios_lidera.clear()
    user.save()
    try:
        from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
        for token in OutstandingToken.objects.filter(user=user):
            BlacklistedToken.objects.get_or_create(token=token)
    except Exception:
        pass
    return user


@transaction.atomic
def cambiar_rol_usuario(user: User, nuevo_rol: str) -> User:
    """Cambia el rol de un usuario"""
    if nuevo_rol == 'lider_ministerio':
        ministerios_ids = list(user.ministerios_lidera.values_list('id', flat=True))
        _validar_asignacion_ministerios(user, ministerios_ids, rol=nuevo_rol)

    user.rol = nuevo_rol
    user.save()
    return user


@transaction.atomic
def asignar_ministerios_usuario(user: User, ministerios_ids: list[int]) -> User:
    """Asigna los ministerios que lidera un usuario"""
    _validar_asignacion_ministerios(user, ministerios_ids, rol=user.rol)
    _sincronizar_miembros(user, ministerios_ids)
    ministerios = Ministerio.objects.filter(id__in=ministerios_ids)
    user.ministerios_lidera.set(ministerios)
    user.save()
    return user
