from django.db import transaction
from django.utils import timezone
from apps.secretaria.models import ComunicadoInterno, LecturaComunicado


@transaction.atomic
def crear_comunicado(creado_por, ministerios_ids=None, **kwargs) -> ComunicadoInterno:
    comunicado = ComunicadoInterno.objects.create(creado_por=creado_por, **kwargs)
    if ministerios_ids:
        comunicado.ministerios_destino.set(ministerios_ids)
    return comunicado


@transaction.atomic
def actualizar_comunicado(comunicado: ComunicadoInterno, ministerios_ids=None, **kwargs) -> ComunicadoInterno:
    for field, value in kwargs.items():
        setattr(comunicado, field, value)
    comunicado.save()
    if ministerios_ids is not None:
        comunicado.ministerios_destino.set(ministerios_ids)
    return comunicado


@transaction.atomic
def publicar_comunicado(comunicado: ComunicadoInterno) -> ComunicadoInterno:
    comunicado.publicado = True
    comunicado.fecha_publicacion = timezone.now()
    comunicado.save(update_fields=['publicado', 'fecha_publicacion', 'updated_at'])
    return comunicado


def marcar_leido(comunicado: ComunicadoInterno, usuario) -> LecturaComunicado:
    lectura, _ = LecturaComunicado.objects.get_or_create(
        comunicado=comunicado,
        usuario=usuario,
    )
    return lectura
