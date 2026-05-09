from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import (
    Rol, Permiso, PerfilUsuario, Ministerio, Miembro, CajaMinisterio,
    MovimientoCaja, Inventario, Ofrenda, Asistencia, Evento,
    Cancion, ProgramaAlabanza, LeccionEXPLO, RecursoComunicacion,
    IdeaComunicacion, PlanificacionActividad
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class PerfilUsuarioSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    ministerios_lidera_nombres = serializers.SerializerMethodField()

    class Meta:
        model = PerfilUsuario
        fields = ['id', 'user', 'rol', 'ministerios_lidera', 'ministerios_lidera_nombres', 'telefono', 'foto', 'activo']
        read_only_fields = ['id']

    def get_ministerios_lidera_nombres(self, obj):
        return [m.nombre for m in obj.ministerios_lidera.all()]


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'password_confirm', 'first_name', 'last_name', 'email']

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password_confirm': 'Las contraseñas no coinciden'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UsuarioCompletoSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    rol_display = serializers.CharField(source='get_rol_display', read_only=True)
    ministerios_lidera_detalles = serializers.SerializerMethodField()
    fecha_creacion = serializers.DateTimeField(read_only=True)
    ultimo_login = serializers.DateTimeField(read_only=True)
    creado_por_nombre = serializers.SerializerMethodField()

    class Meta:
        model = PerfilUsuario
        fields = [
            'id', 'user_id', 'username', 'first_name', 'last_name', 'email',
            'rol', 'rol_display', 'ministerios_lidera', 'ministerios_lidera_detalles',
            'permisos_especificos', 'telefono', 'foto', 'activo',
            'fecha_creacion', 'ultimo_login', 'creado_por', 'creado_por_nombre'
        ]
        read_only_fields = ['id', 'fecha_creacion', 'ultimo_login']

    def get_username(self, obj):
        return obj.user.username

    def get_first_name(self, obj):
        return obj.user.first_name

    def get_last_name(self, obj):
        return obj.user.last_name

    def get_email(self, obj):
        return obj.user.email

    def get_ministerios_lidera_detalles(self, obj):
        return [{'id': m.id, 'nombre': m.nombre, 'slug': m.slug} for m in obj.ministerios_lidera.all()]

    def get_creado_por_nombre(self, obj):
        if obj.creado_por:
            return obj.creado_por.get_full_name() or obj.creado_por.username
        return None


class UsuarioCreateSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    rol = serializers.ChoiceField(choices=PerfilUsuario.ROLES)
    ministerios_lidera = serializers.ListField(child=serializers.IntegerField(), required=False, default=[])
    permisos_especificos = serializers.JSONField(required=False, default=dict)
    telefono = serializers.CharField(max_length=20, required=False, allow_blank=True)
    activo = serializers.BooleanField(default=True)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('El nombre de usuario ya existe')
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('El email ya está en uso')
        return value

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError({'password_confirm': 'Las contraseñas no coinciden'})
        return attrs


class UsuarioUpdateSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)
    email = serializers.EmailField(required=False)
    rol = serializers.ChoiceField(choices=PerfilUsuario.ROLES, required=False)
    ministerios_lidera = serializers.ListField(child=serializers.IntegerField(), required=False)
    permisos_especificos = serializers.JSONField(required=False)
    telefono = serializers.CharField(max_length=20, required=False, allow_blank=True)
    activo = serializers.BooleanField(required=False)
    password_nueva = serializers.CharField(write_only=True, required=False, allow_blank=True)

    def validate_email(self, value):
        user = self.context.get('user')
        if User.objects.exclude(pk=user.user.pk).filter(email=value).exists():
            raise serializers.ValidationError('El email ya está en uso')
        return value


class PermisoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permiso
        fields = ['id', 'nombre', 'modulo', 'acciones']
        read_only_fields = ['id']


class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = ['id', 'nombre', 'descripcion', 'permisos']


class MinisterioSerializer(serializers.ModelSerializer):
    miembros_count = serializers.IntegerField(read_only=True)
    lideres_nombres = serializers.SerializerMethodField()

    class Meta:
        model = Ministerio
        fields = [
            'id', 'nombre', 'slug', 'descripcion', 'color', 'icono', 'activo',
            'miembros_count', 'lideres_nombres', 'fecha_creacion', 'fecha_actualizacion'
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion']

    def get_lideres_nombres(self, obj):
        return [l.user.get_full_name() for l in obj.lideres.all()]


class MiembroSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.CharField(read_only=True)
    ministry_nombre = serializers.CharField(source='ministry.nombre', read_only=True)

    class Meta:
        model = Miembro
        fields = [
            'id', 'ministry', 'ministry_nombre', 'usuario', 'primer_nombre', 'segundo_nombre',
            'primer_apellido', 'segundo_apellido', 'nombre_completo', 'fecha_nacimiento',
            'edad', 'estado_civil', 'telefono', 'email', 'direccion', 'clase',
            'rol_en_ministerio', 'observaciones', 'activo', 'fecha_ingreso', 'fecha_actualizacion'
        ]
        read_only_fields = ['id', 'fecha_ingreso', 'fecha_actualizacion']


class MovimientoCajaSerializer(serializers.ModelSerializer):
    registrado_por_nombre = serializers.CharField(source='registrado_por.get_full_name', read_only=True)

    class Meta:
        model = MovimientoCaja
        fields = [
            'id', 'caja', 'tipo', 'monto', 'descripcion', 'fecha', 'imagen',
            'registrado_por', 'registrado_por_nombre', 'enviado_tesoreria', 'created_at'
        ]
        read_only_fields = ['id', 'fecha', 'created_at']


class CajaMinisterioSerializer(serializers.ModelSerializer):
    movimientos = MovimientoCajaSerializer(many=True, read_only=True)
    saldo_calculado = serializers.SerializerMethodField()
    ministry_nombre = serializers.CharField(source='ministry.nombre', read_only=True)

    class Meta:
        model = CajaMinisterio
        fields = [
            'id', 'ministry', 'ministry_nombre', 'saldo_actual', 'saldo_calculado',
            'movimientos', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_saldo_calculado(self, obj):
        return obj.calcular_saldo()


class InventarioSerializer(serializers.ModelSerializer):
    ministry_nombre = serializers.CharField(source='ministry.nombre', read_only=True)

    class Meta:
        model = Inventario
        fields = [
            'id', 'ministry', 'ministry_nombre', 'nombre', 'categoria', 'cantidad',
            'ubicacion', 'descripcion', 'estado', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class OfrendaSerializer(serializers.ModelSerializer):
    ministry_nombre = serializers.CharField(source='ministry.nombre', read_only=True)

    class Meta:
        model = Ofrenda
        fields = [
            'id', 'ministry', 'ministry_nombre', 'fecha', 'monto', 'clase',
            'envidada_tesoreria', 'fecha_envio', 'observaciones', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AsistenciaSerializer(serializers.ModelSerializer):
    miembro_nombre = serializers.CharField(source='miembro.nombre_completo', read_only=True)
    ministry_nombre = serializers.CharField(source='ministry.nombre', read_only=True)

    class Meta:
        model = Asistencia
        fields = [
            'id', 'ministry', 'ministry_nombre', 'fecha', 'miembro', 'miembro_nombre',
            'presente', 'es_visita', 'nombre_visita', 'clase', 'tiene_biblia',
            'observaciones', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class EventoSerializer(serializers.ModelSerializer):
    ministry_nombre = serializers.CharField(source='ministry.nombre', read_only=True)
    ministerios_relacionados_nombres = serializers.SerializerMethodField()
    creado_por_nombre = serializers.CharField(source='creado_por.get_full_name', read_only=True)

    class Meta:
        model = Evento
        fields = [
            'id', 'ministry', 'ministry_nombre', 'titulo', 'descripcion',
            'fecha_inicio', 'hora_inicio', 'fecha_fin', 'hora_fin', 'ubicacion',
            'tipo', 'ministerios_relacionados', 'ministerios_relacionados_nombres',
            'creado_por', 'creado_por_nombre', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_ministerios_relacionados_nombres(self, obj):
        return [m.nombre for m in obj.ministerios_relacionados.all()]


class CancionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cancion
        fields = [
            'id', 'titulo', 'artista', 'categoria', 'tono', 'letra',
            'acordes', 'link_youtube', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProgramaAlabanzaSerializer(serializers.ModelSerializer):
    ministry_nombre = serializers.CharField(source='ministry.nombre', read_only=True)
    creado_por_nombre = serializers.CharField(source='creado_por.get_full_name', read_only=True)

    class Meta:
        model = ProgramaAlabanza
        fields = [
            'id', 'ministry', 'ministry_nombre', 'fecha', 'alabanzas',
            'creado_por', 'creado_por_nombre', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class LeccionEXPLOSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeccionEXPLO
        fields = [
            'id', 'titulo', 'descripcion', 'contenido', 'link_material',
            'archivo', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class RecursoComunicacionSerializer(serializers.ModelSerializer):
    ministry_nombre = serializers.CharField(source='ministry.nombre', read_only=True)

    class Meta:
        model = RecursoComunicacion
        fields = [
            'id', 'ministry', 'ministry_nombre', 'titulo', 'tipo', 'descripcion',
            'archivo', 'url_externa', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class IdeaComunicacionSerializer(serializers.ModelSerializer):
    ministry_nombre = serializers.CharField(source='ministry.nombre', read_only=True)

    class Meta:
        model = IdeaComunicacion
        fields = [
            'id', 'ministry', 'ministry_nombre', 'titulo', 'descripcion',
            'prioridad', 'completada', 'fecha_completada', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class PlanificacionActividadSerializer(serializers.ModelSerializer):
    ministry_nombre = serializers.CharField(source='ministry.nombre', read_only=True)
    ministerios_relacionados_nombres = serializers.SerializerMethodField()
    responsable_nombre = serializers.CharField(source='responsable.get_full_name', read_only=True)

    class Meta:
        model = PlanificacionActividad
        fields = [
            'id', 'ministry', 'ministry_nombre', 'titulo', 'descripcion',
            'fecha_planificada', 'hora', 'ubicacion', 'tipo',
            'ministerios_relacionados', 'ministerios_relacionados_nombres',
            'responsable', 'responsable_nombre', 'presupuesto', 'estado',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_ministerios_relacionados_nombres(self, obj):
        return [m.nombre for m in obj.ministerios_relacionados.all()]


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)