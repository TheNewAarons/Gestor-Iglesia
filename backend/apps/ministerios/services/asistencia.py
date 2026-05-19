from django.db import transaction
from ..models import Asistencia, Miembro


@transaction.atomic
def registrar_asistencia(ministry, **kwargs) -> Asistencia:
    """Registra una entrada de asistencia"""
    asistencia = Asistencia.objects.create(ministry=ministry, **kwargs)
    return asistencia


@transaction.atomic
def actualizar_asistencia(asistencia: Asistencia, **kwargs) -> Asistencia:
    """Actualiza un registro de asistencia"""
    for field, value in kwargs.items():
        setattr(asistencia, field, value)
    asistencia.save()
    return asistencia


@transaction.atomic
def registrar_asistencia_lote(ministry, fecha, registros: list[dict]) -> list[Asistencia]:
    """Registra múltiples asistencias en lote para un día"""
    asistencias = []
    for registro in registros:
        asistencia = Asistencia.objects.create(
            ministry=ministry, fecha=fecha, **registro
        )
        asistencias.append(asistencia)
    return asistencias
