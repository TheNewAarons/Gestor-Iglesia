from django.db.models import Q
from datetime import date
from django.contrib.auth import get_user_model
from ..models import Miembro, Ministerio

User = get_user_model()


def _sincronizar_usuarios_como_miembros(ministry):
    """Asegura que todos los usuarios en ministerios_lidera tengan su registro Miembro"""
    users = ministry.lideres.filter(is_active=True)
    existing_user_ids = set(
        Miembro.objects.filter(ministry=ministry, usuario__isnull=False)
        .values_list('usuario_id', flat=True)
    )
    for user in users:
        if user.id not in existing_user_ids:
            rol_en_ministerio = 'lider' if user.rol == 'lider_ministerio' else 'miembro'
            Miembro.objects.create(
                ministry=ministry,
                usuario=user,
                primer_nombre=user.first_name or user.username,
                primer_apellido=user.last_name or '',
                email=user.email or '',
                telefono=user.telefono or '',
                rol_en_ministerio=rol_en_ministerio,
                origen='sistema',
                activo=True,
            )


def listar_miembros(filters: dict = None):
    """Lista miembros con filtros opcionales"""
    queryset = Miembro.objects.select_related('ministry').filter(activo=True)

    if filters:
        if ministry_slug := filters.get('ministerio'):
            queryset = queryset.filter(ministry__slug=ministry_slug)
        if clase := filters.get('clase'):
            queryset = queryset.filter(clase=clase)
        if estado_civil := filters.get('estado_civil'):
            queryset = queryset.filter(estado_civil=estado_civil)
        if search := filters.get('search'):
            queryset = queryset.filter(
                Q(primer_nombre__icontains=search) |
                Q(segundo_nombre__icontains=search) |
                Q(primer_apellido__icontains=search) |
                Q(segundo_apellido__icontains=search)
            )

    return queryset


def listar_miembros_por_ministerio(ministry: Ministerio, clase: str = None):
    """Lista miembros de un ministerio específico, sincronizando usuarios asignados"""
    _sincronizar_usuarios_como_miembros(ministry)
    queryset = ministry.miembros.select_related('usuario').filter(activo=True)
    if clase:
        queryset = queryset.filter(clase=clase)
    return queryset


def obtener_miembro(pk: int):
    """Obtiene un miembro por ID"""
    try:
        return Miembro.objects.select_related('ministry', 'usuario').get(pk=pk)
    except Miembro.DoesNotExist:
        return None


def listar_cumpleanos_del_mes(ministry_slug: str = None):
    """Lista miembros con cumpleaños este mes"""
    today = date.today()
    mes_actual = today.month

    miembros = Miembro.objects.filter(
        activo=True,
        fecha_nacimiento__month=mes_actual
    )

    if ministry_slug:
        miembros = miembros.filter(ministry__slug=ministry_slug)

    miembros = miembros.order_by('fecha_nacimiento__day')

    resultado = []
    for m in miembros:
        dias_faltantes = (m.fecha_nacimiento.replace(year=today.year) - today).days
        resultado.append({
            'id': m.id,
            'nombre_completo': m.nombre_completo,
            'fecha_nacimiento': m.fecha_nacimiento,
            'dia': m.fecha_nacimiento.day,
            'dias_faltantes': dias_faltantes if dias_faltantes >= 0 else 365 + dias_faltantes
        })

    return resultado
