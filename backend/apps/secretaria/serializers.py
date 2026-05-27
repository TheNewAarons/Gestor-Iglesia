from rest_framework import serializers
from apps.secretaria.models import (
    ActaReunion, SolicitudTramite, VisitaIglesia,
    ComunicadoInterno, LecturaComunicado, HistorialEstadoMiembro,
    ConfiguracionWhatsApp, MensajeWhatsApp, EnvioWhatsAppLog,
)


class ActaReunionSerializer(serializers.ModelSerializer):
    creado_por_nombre = serializers.SerializerMethodField()
    aprobada_por_nombre = serializers.SerializerMethodField()
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)

    class Meta:
        model = ActaReunion
        fields = [
            'id', 'titulo', 'tipo', 'tipo_display', 'fecha_reunion', 'hora_reunion',
            'lugar', 'presidida_por', 'asistentes', 'orden_del_dia', 'acuerdos',
            'observaciones', 'estado', 'estado_display', 'aprobada_en',
            'creado_por', 'creado_por_nombre', 'aprobada_por', 'aprobada_por_nombre',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['creado_por', 'aprobada_por', 'aprobada_en', 'created_at', 'updated_at']

    def get_creado_por_nombre(self, obj):
        return obj.creado_por.get_full_name() or obj.creado_por.username if obj.creado_por else None

    def get_aprobada_por_nombre(self, obj):
        return obj.aprobada_por.get_full_name() or obj.aprobada_por.username if obj.aprobada_por else None


class SolicitudTramiteSerializer(serializers.ModelSerializer):
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    prioridad_display = serializers.CharField(source='get_prioridad_display', read_only=True)
    registrada_por_nombre = serializers.SerializerMethodField()
    atendida_por_nombre = serializers.SerializerMethodField()
    miembro_nombre = serializers.SerializerMethodField()
    ministerio_nombre = serializers.SerializerMethodField()

    class Meta:
        model = SolicitudTramite
        fields = [
            'id', 'tipo', 'tipo_display', 'solicitante_nombre',
            'solicitante_miembro', 'miembro_nombre',
            'ministerio', 'ministerio_nombre',
            'descripcion', 'datos_adicionales',
            'estado', 'estado_display', 'prioridad', 'prioridad_display',
            'fecha_solicitud', 'fecha_resolucion', 'resolucion_notas',
            'atendida_por', 'atendida_por_nombre',
            'registrada_por', 'registrada_por_nombre',
            'documento_generado', 'created_at', 'updated_at',
        ]
        read_only_fields = ['registrada_por', 'fecha_solicitud', 'created_at', 'updated_at']

    def get_registrada_por_nombre(self, obj):
        return obj.registrada_por.get_full_name() if obj.registrada_por else None

    def get_atendida_por_nombre(self, obj):
        return obj.atendida_por.get_full_name() if obj.atendida_por else None

    def get_miembro_nombre(self, obj):
        return obj.solicitante_miembro.nombre_completo if obj.solicitante_miembro else None

    def get_ministerio_nombre(self, obj):
        return obj.ministerio.nombre if obj.ministerio else None

    REQUIRED_FIELDS = {
        'carta_recomendacion': ['iglesia_destino'],
        'transferencia': ['iglesia_origen', 'iglesia_destino'],
        'bautismo': ['fecha_bautismo'],
        'matrimonio': ['nombre_conyuge', 'fecha_ceremonia'],
    }

    def validate(self, data):
        tipo = data.get('tipo')
        adicionales = data.get('datos_adicionales', {})
        required = self.REQUIRED_FIELDS.get(tipo, [])
        missing = [f for f in required if not adicionales.get(f)]
        if missing:
            raise serializers.ValidationError({
                'datos_adicionales': f'Campos requeridos para {tipo}: {", ".join(missing)}'
            })
        return data

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.documento_generado:
            request = self.context.get('request')
            if request:
                data['documento_generado'] = request.build_absolute_uri(
                    instance.documento_generado.url
                )
        return data


class VisitaIglesiaSerializer(serializers.ModelSerializer):
    seguimiento_display = serializers.CharField(source='get_seguimiento_display', read_only=True)
    ministerio_nombre = serializers.SerializerMethodField()
    responsable_nombre = serializers.SerializerMethodField()
    miembro_vinculado_nombre = serializers.SerializerMethodField()

    class Meta:
        model = VisitaIglesia
        fields = [
            'id', 'nombre', 'telefono', 'email', 'direccion',
            'fecha_primera_visita', 'cantidad_visitas', 'ultima_visita',
            'ministerio_interes', 'ministerio_nombre',
            'seguimiento', 'seguimiento_display',
            'responsable_seguimiento', 'responsable_nombre',
            'notas', 'convertido_miembro',
            'miembro_vinculado', 'miembro_vinculado_nombre',
            'activo', 'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_ministerio_nombre(self, obj):
        return obj.ministerio_interes.nombre if obj.ministerio_interes else None

    def get_responsable_nombre(self, obj):
        return obj.responsable_seguimiento.get_full_name() if obj.responsable_seguimiento else None

    def get_miembro_vinculado_nombre(self, obj):
        return obj.miembro_vinculado.nombre_completo if obj.miembro_vinculado else None


class LecturaComunicadoSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.SerializerMethodField()

    class Meta:
        model = LecturaComunicado
        fields = ['id', 'usuario', 'usuario_nombre', 'leido_en']

    def get_usuario_nombre(self, obj):
        return obj.usuario.get_full_name() or obj.usuario.username


class ComunicadoInternoSerializer(serializers.ModelSerializer):
    creado_por_nombre = serializers.SerializerMethodField()
    destinatarios_display = serializers.CharField(source='get_destinatarios_display', read_only=True)
    ministerios_destino_nombres = serializers.SerializerMethodField()
    total_lecturas = serializers.SerializerMethodField()

    class Meta:
        model = ComunicadoInterno
        fields = [
            'id', 'titulo', 'contenido',
            'destinatarios', 'destinatarios_display',
            'ministerios_destino', 'ministerios_destino_nombres',
            'roles_destino', 'archivo_adjunto',
            'requiere_confirmacion', 'publicado',
            'fecha_publicacion', 'fecha_vencimiento',
            'creado_por', 'creado_por_nombre',
            'total_lecturas', 'created_at', 'updated_at',
        ]
        read_only_fields = ['creado_por', 'publicado', 'fecha_publicacion', 'created_at', 'updated_at']

    def get_creado_por_nombre(self, obj):
        return obj.creado_por.get_full_name() if obj.creado_por else None

    def get_ministerios_destino_nombres(self, obj):
        return list(obj.ministerios_destino.values_list('nombre', flat=True))

    def get_total_lecturas(self, obj):
        return obj.lecturas.count()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.archivo_adjunto:
            request = self.context.get('request')
            if request:
                data['archivo_adjunto'] = request.build_absolute_uri(
                    instance.archivo_adjunto.url
                )
        return data


class HistorialEstadoMiembroSerializer(serializers.ModelSerializer):
    evento_display = serializers.CharField(source='get_evento_display', read_only=True)
    documentado_por_nombre = serializers.SerializerMethodField()
    miembro_nombre = serializers.SerializerMethodField()

    class Meta:
        model = HistorialEstadoMiembro
        fields = [
            'id', 'miembro', 'miembro_nombre',
            'evento', 'evento_display', 'fecha_evento',
            'descripcion', 'iglesia_origen', 'iglesia_destino',
            'documentado_por', 'documentado_por_nombre',
            'documento_adjunto', 'created_at',
        ]
        read_only_fields = ['documentado_por', 'created_at']

    def get_documentado_por_nombre(self, obj):
        return obj.documentado_por.get_full_name() if obj.documentado_por else None

    def get_miembro_nombre(self, obj):
        return obj.miembro.nombre_completo if obj.miembro else None


class ConfiguracionWhatsAppSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfiguracionWhatsApp
        fields = ['id', 'grupo_jid', 'hora_envio', 'activo', 'rotacion_index', 'updated_at']
        read_only_fields = ['rotacion_index', 'updated_at']


class MensajeWhatsAppSerializer(serializers.ModelSerializer):
    class Meta:
        model = MensajeWhatsApp
        fields = ['id', 'numero', 'texto', 'imagen', 'activo', 'updated_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.imagen:
            request = self.context.get('request')
            if request:
                data['imagen'] = request.build_absolute_uri(instance.imagen.url)
        return data


class EnvioWhatsAppLogSerializer(serializers.ModelSerializer):
    mensaje_numero = serializers.SerializerMethodField()
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)

    class Meta:
        model = EnvioWhatsAppLog
        fields = [
            'id', 'mensaje', 'mensaje_numero', 'texto_enviado',
            'grupo_jid', 'estado', 'estado_display',
            'error_detalle', 'enviado_en',
        ]

    def get_mensaje_numero(self, obj):
        return obj.mensaje.numero if obj.mensaje else None
