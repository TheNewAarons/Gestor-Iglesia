from datetime import time
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class ActaReunion(models.Model):
    TIPO_CHOICES = [
        ('junta_directiva', 'Junta Directiva'),
        ('concilio', 'Concilio'),
        ('comite', 'Comité'),
        ('otra', 'Otra'),
    ]
    ESTADO_CHOICES = [
        ('borrador', 'Borrador'),
        ('aprobada', 'Aprobada'),
        ('archivada', 'Archivada'),
    ]

    titulo = models.CharField(max_length=200)
    tipo = models.CharField(max_length=30, choices=TIPO_CHOICES)
    fecha_reunion = models.DateField()
    hora_reunion = models.TimeField(null=True, blank=True)
    lugar = models.CharField(max_length=200, blank=True)
    presidida_por = models.CharField(max_length=100, blank=True)
    asistentes = models.JSONField(default=list)
    orden_del_dia = models.JSONField(default=list)
    acuerdos = models.JSONField(default=list)
    observaciones = models.TextField(blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='borrador')
    aprobada_en = models.DateTimeField(null=True, blank=True)
    creado_por = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='actas_creadas'
    )
    aprobada_por = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='actas_aprobadas'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-fecha_reunion']
        verbose_name = 'Acta de Reunión'
        verbose_name_plural = 'Actas de Reunión'

    def __str__(self):
        return f"{self.titulo} ({self.fecha_reunion})"


class SolicitudTramite(models.Model):
    TIPO_CHOICES = [
        ('membresia', 'Solicitud de Membresía'),
        ('carta_recomendacion', 'Carta de Recomendación'),
        ('carta_membresia', 'Carta de Membresía'),
        ('transferencia', 'Transferencia de Membresía'),
        ('bautismo', 'Bautismo'),
        ('matrimonio', 'Matrimonio'),
        ('retiro', 'Retiro Voluntario'),
        ('otra', 'Otra Solicitud'),
    ]
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En Proceso'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
    ]
    PRIORIDAD_CHOICES = [
        ('alta', 'Alta'),
        ('media', 'Media'),
        ('baja', 'Baja'),
    ]

    tipo = models.CharField(max_length=30, choices=TIPO_CHOICES)
    solicitante_nombre = models.CharField(max_length=200)
    solicitante_miembro = models.ForeignKey(
        'ministerios.Miembro', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='solicitudes'
    )
    ministerio = models.ForeignKey(
        'ministerios.Ministerio', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='solicitudes_secretaria'
    )
    descripcion = models.TextField(blank=True)
    datos_adicionales = models.JSONField(default=dict)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    prioridad = models.CharField(max_length=10, choices=PRIORIDAD_CHOICES, default='media')
    fecha_solicitud = models.DateField(auto_now_add=True)
    fecha_resolucion = models.DateField(null=True, blank=True)
    resolucion_notas = models.TextField(blank=True)
    atendida_por = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='solicitudes_atendidas'
    )
    registrada_por = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        related_name='solicitudes_registradas'
    )
    documento_generado = models.FileField(
        upload_to='secretaria/solicitudes/', null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Solicitud / Trámite'
        verbose_name_plural = 'Solicitudes / Trámites'

    def __str__(self):
        return f"{self.get_tipo_display()} — {self.solicitante_nombre}"


class VisitaIglesia(models.Model):
    SEGUIMIENTO_CHOICES = [
        ('sin_seguimiento', 'Sin Seguimiento'),
        ('contactado', 'Contactado'),
        ('integrado', 'Integrado a Ministerio'),
        ('no_regreso', 'No Regresó'),
    ]

    nombre = models.CharField(max_length=200)
    telefono = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    direccion = models.TextField(blank=True)
    fecha_primera_visita = models.DateField()
    cantidad_visitas = models.PositiveIntegerField(default=1)
    ultima_visita = models.DateField(null=True, blank=True)
    ministerio_interes = models.ForeignKey(
        'ministerios.Ministerio', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='visitas'
    )
    seguimiento = models.CharField(
        max_length=30, choices=SEGUIMIENTO_CHOICES, default='sin_seguimiento'
    )
    responsable_seguimiento = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='visitas_asignadas'
    )
    notas = models.TextField(blank=True)
    convertido_miembro = models.BooleanField(default=False)
    miembro_vinculado = models.OneToOneField(
        'ministerios.Miembro', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='visita_origen'
    )
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-fecha_primera_visita']
        verbose_name = 'Visita'
        verbose_name_plural = 'Visitas'

    def __str__(self):
        return self.nombre


class ComunicadoInterno(models.Model):
    DESTINATARIO_CHOICES = [
        ('todos', 'Todos'),
        ('lideres', 'Líderes'),
        ('ministerio', 'Ministerio Específico'),
        ('roles', 'Por Roles'),
    ]

    titulo = models.CharField(max_length=200)
    contenido = models.TextField()
    destinatarios = models.CharField(
        max_length=30, choices=DESTINATARIO_CHOICES, default='todos'
    )
    ministerios_destino = models.ManyToManyField(
        'ministerios.Ministerio', blank=True, related_name='comunicados'
    )
    roles_destino = models.JSONField(default=list)
    archivo_adjunto = models.FileField(
        upload_to='secretaria/comunicados/', null=True, blank=True
    )
    requiere_confirmacion = models.BooleanField(default=False)
    publicado = models.BooleanField(default=False)
    fecha_publicacion = models.DateTimeField(null=True, blank=True)
    fecha_vencimiento = models.DateField(null=True, blank=True)
    creado_por = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='comunicados_creados'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Comunicado Interno'
        verbose_name_plural = 'Comunicados Internos'

    def __str__(self):
        return self.titulo


class LecturaComunicado(models.Model):
    comunicado = models.ForeignKey(
        ComunicadoInterno, on_delete=models.CASCADE, related_name='lecturas'
    )
    usuario = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='lecturas_comunicados'
    )
    leido_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['comunicado', 'usuario']
        verbose_name = 'Lectura de Comunicado'

    def __str__(self):
        return f"{self.usuario} leyó {self.comunicado}"


class HistorialEstadoMiembro(models.Model):
    EVENTO_CHOICES = [
        ('ingreso', 'Ingreso'),
        ('transferencia_entrada', 'Transferencia Entrada'),
        ('transferencia_salida', 'Transferencia Salida'),
        ('bautismo', 'Bautismo'),
        ('disciplina', 'Proceso Disciplinario'),
        ('restauracion', 'Restauración'),
        ('retiro_voluntario', 'Retiro Voluntario'),
        ('fallecimiento', 'Fallecimiento'),
        ('otra', 'Otra Anotación'),
    ]

    miembro = models.ForeignKey(
        'ministerios.Miembro', on_delete=models.CASCADE, related_name='historial_estado'
    )
    evento = models.CharField(max_length=30, choices=EVENTO_CHOICES)
    fecha_evento = models.DateField()
    descripcion = models.TextField(blank=True)
    iglesia_origen = models.CharField(max_length=200, blank=True)
    iglesia_destino = models.CharField(max_length=200, blank=True)
    documentado_por = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='historial_documentado'
    )
    documento_adjunto = models.FileField(
        upload_to='secretaria/historial/', null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_evento']
        verbose_name = 'Historial de Estado de Miembro'
        verbose_name_plural = 'Historial de Estados de Miembro'

    def __str__(self):
        return f"{self.miembro} — {self.get_evento_display()} ({self.fecha_evento})"


class ConfiguracionWhatsApp(models.Model):
    grupo_jid = models.CharField(max_length=100, blank=True)
    hora_envio = models.TimeField(default=time(9, 0))
    activo = models.BooleanField(default=False)
    rotacion_index = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Configuración WhatsApp'

    @classmethod
    def obtener(cls):
        obj, _ = cls.objects.get_or_create(id=1)
        return obj

    def __str__(self):
        return f"Config WhatsApp (activo={self.activo})"


class MensajeWhatsApp(models.Model):
    numero = models.PositiveSmallIntegerField(unique=True)
    texto = models.TextField()
    imagen = models.ImageField(upload_to='secretaria/whatsapp/', null=True, blank=True)
    activo = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['numero']
        verbose_name = 'Mensaje WhatsApp'
        verbose_name_plural = 'Mensajes WhatsApp'

    def __str__(self):
        return f"Mensaje #{self.numero}"


class EnvioWhatsAppLog(models.Model):
    ESTADO_CHOICES = [
        ('exitoso', 'Exitoso'),
        ('fallido', 'Fallido'),
    ]

    mensaje = models.ForeignKey(
        MensajeWhatsApp, on_delete=models.SET_NULL, null=True, related_name='envios'
    )
    texto_enviado = models.TextField()
    grupo_jid = models.CharField(max_length=100)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES)
    error_detalle = models.TextField(blank=True)
    enviado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-enviado_en']
        verbose_name = 'Log de Envío WhatsApp'
        verbose_name_plural = 'Logs de Envíos WhatsApp'

    def __str__(self):
        return f"Envío {self.estado} — {self.enviado_en}"
