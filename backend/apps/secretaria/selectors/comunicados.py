from apps.secretaria.models import ComunicadoInterno, LecturaComunicado


def listar_comunicados(publicado=None):
    qs = ComunicadoInterno.objects.select_related('creado_por').prefetch_related(
        'ministerios_destino', 'lecturas'
    )
    if publicado is not None:
        qs = qs.filter(publicado=publicado)
    return qs


def comunicados_para_usuario(usuario):
    qs = ComunicadoInterno.objects.filter(publicado=True).select_related('creado_por')
    # Filtrar por destinatario si no es admin/pastora
    if usuario.rol not in ('admin', 'pastora'):
        from django.db.models import Q
        qs = qs.filter(
            Q(destinatarios='todos') |
            Q(destinatarios='roles', roles_destino__contains=usuario.rol) |
            Q(destinatarios='ministerio', ministerios_destino__in=usuario.ministerios_lidera.all()) |
            Q(destinatarios='lideres', roles_destino__contains='lider_ministerio')
        ).distinct()
    return qs


def lecturas_de_comunicado(comunicado_id: int):
    return LecturaComunicado.objects.filter(comunicado_id=comunicado_id).select_related('usuario')
