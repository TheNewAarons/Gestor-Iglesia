from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils.text import slugify


class User(AbstractUser):
    """Modelo de usuario personalizado con roles y permisos"""
    ROLES = [
        ('admin', 'Admin'),
        ('pastora', 'Pastora'),
        ('secretaria', 'Secretaria'),
        ('tesorera', 'Tesorera'),
        ('lider_ministerio', 'Líder de Ministerio'),
        ('concilio', 'Concilio'),
    ]

    rol = models.CharField(max_length=20, choices=ROLES, default='concilio')
    ministerios_lidera = models.ManyToManyField('Ministerio', blank=True, related_name='lideres')
    permisos_especificos = models.JSONField(default=dict, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    foto = models.ImageField(upload_to='usuarios/fotos/', blank=True, null=True)
    creado_por = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True, related_name='usuarios_creados'
    )

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['first_name', 'last_name']

    def __str__(self):
        if self.get_full_name():
            return f"{self.get_full_name()} ({self.username})"
        return self.username

    def tiene_permiso(self, modulo: str, accion: str) -> bool:
        """Verifica si el usuario tiene un permiso específico"""
        if self.rol == 'admin':
            return True

        rol_permisos = {
            'pastora': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True, 'registrar': True, 'exportar': True},
            'secretaria': {'miembros': ['ver', 'crear', 'editar'], 'asistencia': ['ver', 'registrar'], 'eventos': ['ver', 'crear', 'editar']},
            'tesorera': {'caja': ['ver', 'crear', 'editar', 'aprobar'], 'ofrendas': ['ver', 'crear', 'editar'], 'reportes': ['ver', 'exportar']},
            'concilio': {'ver': True},
        }

        permisos = rol_permisos.get(self.rol, {})
        if isinstance(permisos, dict):
            if permisos.get('ver') is True:
                return True
            modulo_permisos = permisos.get(modulo, [])
            return accion in modulo_permisos

        return False


class Rol(models.Model):
    """Roles de usuarios en el sistema"""
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True)
    permisos = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'

    def __str__(self):
        return self.nombre


class Permiso(models.Model):
    """Permisos granulares por módulo para usuarios"""
    MODULOS = [
        ('miembros', 'Miembros'),
        ('asistencia', 'Asistencia'),
        ('caja', 'Caja'),
        ('inventario', 'Inventario'),
        ('eventos', 'Eventos'),
        ('planificaciones', 'Planificaciones'),
        ('usuarios', 'Gestión de Usuarios'),
        ('reportes', 'Reportes'),
        ('ofrendas', 'Ofrendas'),
    ]

    ACCIONES = [
        ('ver', 'Ver'),
        ('crear', 'Crear'),
        ('editar', 'Editar'),
        ('eliminar', 'Eliminar'),
        ('aprobar', 'Aprobar'),
        ('registrar', 'Registrar'),
        ('exportar', 'Exportar'),
    ]

    nombre = models.CharField(max_length=50)
    modulo = models.CharField(max_length=30, choices=MODULOS)
    acciones = models.JSONField(default=list)

    class Meta:
        verbose_name = 'Permiso'
        verbose_name_plural = 'Permisos'
        unique_together = ['nombre', 'modulo']

    def __str__(self):
        return f"{self.nombre} - {self.modulo}"


class Ministerio(models.Model):
    """Ministerios de la iglesia"""
    nombre = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    descripcion = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#3B82F6')
    icono = models.CharField(max_length=50, default='church')
    logo = models.CharField(max_length=200, blank=True, null=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Ministerio'
        verbose_name_plural = 'Ministerios'
        ordering = ['nombre']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre

    @property
    def miembros_activos(self):
        return self.miembros.filter(activo=True).count()


class Miembro(models.Model):
    """Miembros de cada ministerio"""
    ESTADOS_CIVILES = [
        ('soltero', 'Soltero/a'),
        ('casado', 'Casado/a'),
        ('viudo', 'Viudo/a'),
        ('divorciado', 'Divorciado/a'),
    ]

    CLASES_DNI = [
        ('parvulos', 'Párvulos (1-5 años)'),
        ('principiantes', 'Principiantes (6-10 años)'),
        ('primarios', 'Primarios (11-15 años)'),
        ('jovenes', 'Jóvenes (16-35 años)'),
        ('adultos', 'Adultos (35+ años)'),
    ]

    ROLES_MINISTERIO = [
        ('miembro', 'Miembro'),
        ('lider', 'Líder'),
        ('sublider', 'Sublíder'),
        ('tesorero', 'Tesorero'),
        ('secretario', 'Secretario'),
    ]

    ministry = models.ForeignKey(Ministerio, on_delete=models.CASCADE, related_name='miembros')
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='miembros_en_ministerios'
    )

    primer_nombre = models.CharField(max_length=50)
    segundo_nombre = models.CharField(max_length=50, blank=True)
    primer_apellido = models.CharField(max_length=50)
    segundo_apellido = models.CharField(max_length=50, blank=True)

    @property
    def nombre_completo(self):
        segundo_nombre = f" {self.segundo_nombre}" if self.segundo_nombre else ""
        segundo_apellido = f" {self.segundo_apellido}" if self.segundo_apellido else ""
        return f"{self.primer_nombre}{segundo_nombre} {self.primer_apellido}{segundo_apellido}"

    fecha_nacimiento = models.DateField(null=True, blank=True)
    edad = models.PositiveIntegerField(null=True, blank=True)
    estado_civil = models.CharField(max_length=20, choices=ESTADOS_CIVILES, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    direccion = models.TextField(blank=True)

    clase = models.CharField(max_length=20, choices=CLASES_DNI, blank=True, help_text='Solo para DNI')
    rol_en_ministerio = models.CharField(max_length=20, choices=ROLES_MINISTERIO, default='miembro')

    observaciones = models.TextField(blank=True)
    origen = models.CharField(max_length=20, choices=[('manual', 'Manual'), ('sistema', 'Sistema')], default='manual', blank=True)
    activo = models.BooleanField(default=True)
    fecha_ingreso = models.DateField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Miembro'
        verbose_name_plural = 'Miembros'
        ordering = ['primer_apellido', 'primer_nombre']

    def __str__(self):
        return self.nombre_completo


class CajaMinisterio(models.Model):
    """Caja de cada ministerio"""
    ministry = models.OneToOneField(Ministerio, on_delete=models.CASCADE, related_name='caja')
    saldo_actual = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Caja de Ministerio'
        verbose_name_plural = 'Cajas de Ministerios'

    def __str__(self):
        return f"Caja - {self.ministry.nombre}"

    def calcular_saldo(self):
        ingresos = sum(m.monto for m in self.movimientos.filter(tipo='ingreso', aprobado=True))
        egresos = sum(m.monto for m in self.movimientos.filter(tipo='egreso', aprobado=True))
        return ingresos - egresos


class MovimientoCaja(models.Model):
    """Movimientos de la caja del ministerio"""
    TIPOS = [
        ('ingreso', 'Ingreso'),
        ('egreso', 'Egreso'),
    ]

    caja = models.ForeignKey(CajaMinisterio, on_delete=models.CASCADE, related_name='movimientos')
    tipo = models.CharField(max_length=10, choices=TIPOS)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    descripcion = models.TextField(blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    imagen = models.ImageField(upload_to='cajas/boletas/', blank=True, null=True)
    registrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    enviado_tesoreria = models.BooleanField(default=False)
    aprobado = models.BooleanField(default=False)
    ofrenda_origen = models.ForeignKey(
        'Ofrenda', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='movimientos_caja'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Movimiento de Caja'
        verbose_name_plural = 'Movimientos de Caja'
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.tipo} - {self.monto} - {self.caja.ministry.nombre}"


class Inventario(models.Model):
    """Inventario de artículos del ministerio"""
    CATEGORIAS = [
        ('muebles', 'Muebles'),
        ('electronicos', 'Electrónicos'),
        ('decoracion', 'Decoración'),
        ('utensilios', 'Utensilios'),
        ('musica', 'Música'),
        ('otro', 'Otro'),
    ]

    ESTADOS = [
        ('nuevo', 'Nuevo'),
        ('bueno', 'Bueno'),
        ('regular', 'Regular'),
        ('mal_estado', 'Mal Estado'),
    ]

    ministry = models.ForeignKey(Ministerio, on_delete=models.CASCADE, related_name='inventario')
    nombre = models.CharField(max_length=100)
    categoria = models.CharField(max_length=20, choices=CATEGORIAS)
    cantidad = models.PositiveIntegerField(default=1)
    ubicacion = models.CharField(max_length=100, blank=True)
    descripcion = models.TextField(blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='bueno')
    imagen = models.ImageField(upload_to='inventario/fotos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Inventario'
        verbose_name_plural = 'Inventarios'
        ordering = ['categoria', 'nombre']

    def __str__(self):
        return f"{self.nombre} ({self.cantidad}) - {self.ministry.nombre}"


class Ofrenda(models.Model):
    """Registro de ofrendas por ministry"""
    CATEGORIAS_MNI = [
        ('ofrenda_general', 'Ofrenda General'),
        ('caja_alabastro', 'Caja de Alabastro'),
        ('accion_gracias', 'Acción de Gracias'),
        ('dip', 'DIP'),
        ('oracion_ayuno', 'Oración y Ayuno'),
        ('fem', 'FEM'),
        ('otros', 'Otros'),
    ]

    ministry = models.ForeignKey(Ministerio, on_delete=models.CASCADE, related_name='ofrendas')
    fecha = models.DateField()
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    categoria = models.CharField(max_length=30, choices=CATEGORIAS_MNI, blank=True, help_text='Categoría de ofrenda (MNI)')
    clase = models.CharField(max_length=30, blank=True, help_text='Para DNI - clase específica')
    movimiento_tesoreria = models.ForeignKey('tesoreria.MovimientoTesoreria', on_delete=models.SET_NULL, null=True, blank=True, related_name='ofrenda_origen')
    envidada_tesoreria = models.BooleanField(default=False)
    fecha_envio = models.DateTimeField(null=True, blank=True)
    aprobado = models.BooleanField(default=False)
    observaciones = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Ofrenda'
        verbose_name_plural = 'Ofrendas'
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.ministry.nombre} - {self.fecha} - {self.monto}"


class Asistencia(models.Model):
    """Registro de asistencia semanal (especialmente para DNI)"""
    ministry = models.ForeignKey(Ministerio, on_delete=models.CASCADE, related_name='asistencias')
    fecha = models.DateField()
    miembro = models.ForeignKey(Miembro, on_delete=models.CASCADE, related_name='asistencias', null=True, blank=True)
    presente = models.BooleanField(default=False)
    es_visita = models.BooleanField(default=False)
    nombre_visita = models.CharField(max_length=100, blank=True)
    clase = models.CharField(max_length=30, blank=True)
    tiene_biblia = models.BooleanField(default=False, help_text='Indica si el asistente tiene Biblia')
    observaciones = models.TextField(blank=True, help_text='Observaciones adicionales')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Asistencia'
        verbose_name_plural = 'Asistencias'
        ordering = ['-fecha', 'clase']

    def __str__(self):
        nombre = self.miembro.nombre_completo if self.miembro else self.nombre_visita
        return f"{nombre} - {self.fecha} - {'Presente' if self.presente else 'Ausente'}"


class Evento(models.Model):
    """Eventos del calendario"""
    TIPOS = [
        ('propio', 'Propio'),
        ('compartido', 'Compartido'),
    ]

    ministry = models.ForeignKey(Ministerio, on_delete=models.CASCADE, related_name='eventos')
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    fecha_inicio = models.DateTimeField()
    hora_inicio = models.TimeField(null=True, blank=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)
    hora_fin = models.TimeField(null=True, blank=True)
    ubicacion = models.CharField(max_length=200, blank=True)
    tipo = models.CharField(max_length=10, choices=TIPOS, default='propio')
    ministerios_relacionados = models.ManyToManyField(Ministerio, blank=True, related_name='eventos_compartidos')
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'
        ordering = ['fecha_inicio']

    def __str__(self):
        return f"{self.titulo} - {self.fecha_inicio}"


class Cancion(models.Model):
    """Banco de canciones para Alabanza"""
    CATEGORIAS = [
        ('rapida', 'Rápida'),
        ('media', 'Media'),
        ('lenta', 'Lenta'),
    ]

    titulo = models.CharField(max_length=200)
    artista = models.CharField(max_length=100, blank=True)
    categoria = models.CharField(max_length=10, choices=CATEGORIAS)
    tono = models.CharField(max_length=10, blank=True)
    letra = models.TextField(blank=True)
    acordes = models.TextField(blank=True)
    link_youtube = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Canción'
        verbose_name_plural = 'Canciones'
        ordering = ['titulo']

    def __str__(self):
        return self.titulo


class ProgramaAlabanza(models.Model):
    """Programa dominical de alabanzas"""
    ministry = models.ForeignKey(Ministerio, on_delete=models.CASCADE, related_name='programas')
    fecha = models.DateField()
    alabanzas = models.JSONField(default=list, help_text='Lista de canciones ordenadas')
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Programa de Alabanza'
        verbose_name_plural = 'Programas de Alabanza'
        ordering = ['-fecha']

    def __str__(self):
        return f"Programa - {self.fecha}"


class LeccionEXPLO(models.Model):
    """Lecciones para EXPLO"""
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    contenido = models.TextField(blank=True)
    link_material = models.URLField(blank=True)
    archivo = models.FileField(upload_to='explo/lecciones/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Lección EXPLO'
        verbose_name_plural = 'Lecciones EXPLO'
        ordering = ['-created_at']

    def __str__(self):
        return self.titulo


class RecursoComunicacion(models.Model):
    """Recursos gráficos para Comunicaciones"""
    TIPOS = [
        ('colorimetria', 'Colorimetría'),
        ('plantilla', 'Plantilla'),
        ('imagen', 'Imagen'),
        ('video', 'Video'),
        ('logo', 'Logo'),
        ('documento', 'Documento'),
    ]

    ministry = models.ForeignKey(Ministerio, on_delete=models.CASCADE, related_name='recursos')
    titulo = models.CharField(max_length=200)
    tipo = models.CharField(max_length=20, choices=TIPOS)
    descripcion = models.TextField(blank=True)
    archivo = models.FileField(upload_to='comunicaciones/recursos/')
    url_externa = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Recurso de Comunicación'
        verbose_name_plural = 'Recursos de Comunicación'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.titulo} ({self.get_tipo_display()})"


class IdeaComunicacion(models.Model):
    """Checklist de ideas para Comunicaciones"""
    PRIORIDADES = [
        ('alta', 'Alta'),
        ('media', 'Media'),
        ('baja', 'Baja'),
    ]

    ministry = models.ForeignKey(Ministerio, on_delete=models.CASCADE, related_name='ideas')
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    prioridad = models.CharField(max_length=10, choices=PRIORIDADES, default='media')
    completada = models.BooleanField(default=False)
    fecha_completada = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Idea de Comunicación'
        verbose_name_plural = 'Ideas de Comunicación'
        ordering = ['-created_at']

    def __str__(self):
        return self.titulo


class PlanificacionActividad(models.Model):
    """Planificación de actividades propias del ministerio"""
    TIPO_CHOICES = [
        ('propia', 'Propia'),
        ('compartida', 'Compartida'),
    ]

    ESTADO_CHOICES = [
        ('planificada', 'Planificada'),
        ('en_proceso', 'En Proceso'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
    ]

    ministry = models.ForeignKey(Ministerio, on_delete=models.CASCADE, related_name='planificaciones')
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    fecha_planificada = models.DateField()
    hora = models.TimeField(null=True, blank=True)
    ubicacion = models.CharField(max_length=200, blank=True)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='propia')
    ministerios_relacionados = models.ManyToManyField(Ministerio, blank=True, related_name='planificaciones_compartidas')
    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    presupuesto = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='planificada')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Planificación de Actividad'
        verbose_name_plural = 'Planificaciones de Actividades'
        ordering = ['-fecha_planificada']

    def __str__(self):
        return f"{self.titulo} - {self.fecha_planificada}"


class EnfoqueMNI(models.Model):
    mes = models.PositiveSmallIntegerField(unique=True)
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Enfoque MNI'
        verbose_name_plural = 'Enfoques MNI'
        ordering = ['mes']

    def __str__(self):
        MESES = {
            1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
            5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
            9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre',
        }
        return f"{MESES.get(self.mes, self.mes)} — {self.titulo}"


class ProgramaUltimoDomingo(models.Model):
    ministry = models.ForeignKey(
        Ministerio, on_delete=models.CASCADE, related_name='programas_domingo'
    )
    titulo = models.CharField(max_length=200)
    fecha = models.DateField()
    secciones = models.JSONField(default=dict)
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Programa Último Domingo'
        verbose_name_plural = 'Programas Último Domingo'
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.titulo} — {self.fecha}"


class Nota(models.Model):
    ministry = models.ForeignKey(Ministerio, on_delete=models.CASCADE, related_name='notas')
    titulo = models.CharField(max_length=200)
    contenido = models.TextField(blank=True)
    evento = models.ForeignKey(
        Evento, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='notas', help_text='Evento opcional al que se vincula la nota'
    )
    color = models.CharField(max_length=7, default='#fef3c7')
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Nota'
        verbose_name_plural = 'Notas'
        ordering = ['-updated_at']

    def __str__(self):
        return self.titulo
