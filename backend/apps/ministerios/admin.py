from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from .models import (
    Rol, Ministerio, Miembro, CajaMinisterio,
    MovimientoCaja, Inventario, Ofrenda, Asistencia, Evento,
    Cancion, ProgramaAlabanza, LeccionEXPLO, RecursoComunicacion,
    IdeaComunicacion, PlanificacionActividad
)

User = get_user_model()


@admin.register(User)
class UsuarioAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Datos adicionales', {
            'fields': ('rol', 'ministerios_lidera', 'permisos_especificos',
                       'telefono', 'foto', 'creado_por')
        }),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Datos adicionales', {
            'fields': ('rol', 'ministerios_lidera', 'permisos_especificos',
                       'telefono', 'foto', 'creado_por')
        }),
    )


@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'descripcion']
    search_fields = ['nombre']


@admin.register(Ministerio)
class MinisterioAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'slug', 'color', 'activo', 'fecha_creacion']
    list_filter = ['activo']
    search_fields = ['nombre', 'descripcion']
    prepopulated_fields = {'slug': ('nombre',)}


@admin.register(Miembro)
class MiembroAdmin(admin.ModelAdmin):
    list_display = ['nombre_completo', 'ministry', 'rol_en_ministerio', 'clase', 'activo']
    list_filter = ['ministry', 'rol_en_ministerio', 'clase', 'estado_civil', 'activo']
    search_fields = ['primer_nombre', 'segundo_nombre', 'primer_apellido', 'segundo_apellido']
    date_hierarchy = 'fecha_ingreso'


@admin.register(CajaMinisterio)
class CajaMinisterioAdmin(admin.ModelAdmin):
    list_display = ['ministry', 'saldo_actual', 'updated_at']
    search_fields = ['ministry__nombre']


@admin.register(MovimientoCaja)
class MovimientoCajaAdmin(admin.ModelAdmin):
    list_display = ['caja', 'tipo', 'monto', 'descripcion', 'fecha', 'enviado_tesoreria']
    list_filter = ['tipo', 'enviado_tesoreria', 'fecha']
    search_fields = ['descripcion']
    date_hierarchy = 'fecha'


@admin.register(Inventario)
class InventarioAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'ministry', 'categoria', 'cantidad', 'estado']
    list_filter = ['ministry', 'categoria', 'estado']
    search_fields = ['nombre']


@admin.register(Ofrenda)
class OfrendaAdmin(admin.ModelAdmin):
    list_display = ['ministry', 'fecha', 'monto', 'clase', 'envidada_tesoreria']
    list_filter = ['ministry', 'envidada_tesoreria', 'fecha']
    search_fields = ['observaciones']
    date_hierarchy = 'fecha'


@admin.register(Asistencia)
class AsistenciaAdmin(admin.ModelAdmin):
    list_display = ['miembro', 'ministry', 'fecha', 'presente', 'es_visita', 'clase']
    list_filter = ['ministry', 'fecha', 'presente', 'es_visita']
    date_hierarchy = 'fecha'


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'ministry', 'fecha_inicio', 'tipo']
    list_filter = ['ministry', 'tipo', 'fecha_inicio']
    search_fields = ['titulo', 'descripcion']
    date_hierarchy = 'fecha_inicio'


@admin.register(Cancion)
class CancionAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'artista', 'categoria', 'tono']
    list_filter = ['categoria']
    search_fields = ['titulo', 'artista']


@admin.register(ProgramaAlabanza)
class ProgramaAlabanzaAdmin(admin.ModelAdmin):
    list_display = ['ministry', 'fecha', 'created_at']
    list_filter = ['ministry', 'fecha']
    date_hierarchy = 'fecha'


@admin.register(LeccionEXPLO)
class LeccionEXPLOAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'created_at']
    search_fields = ['titulo', 'descripcion']
    date_hierarchy = 'created_at'


@admin.register(RecursoComunicacion)
class RecursoComunicacionAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'ministry', 'tipo', 'created_at']
    list_filter = ['ministry', 'tipo']
    search_fields = ['titulo', 'descripcion']


@admin.register(IdeaComunicacion)
class IdeaComunicacionAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'ministry', 'prioridad', 'completada']
    list_filter = ['ministry', 'prioridad', 'completada']
    search_fields = ['titulo', 'descripcion']


@admin.register(PlanificacionActividad)
class PlanificacionActividadAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'ministry', 'fecha_planificada', 'estado']
    list_filter = ['ministry', 'estado', 'tipo']
    search_fields = ['titulo', 'descripcion']
    date_hierarchy = 'fecha_planificada'
