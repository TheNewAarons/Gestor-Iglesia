from rest_framework import serializers
from .models import ConfiguracionFinanzas, InformeMensual, MovimientoTesoreria, CuotaFija
from apps.ministerios.serializers import MovimientoCajaSerializer


class ConfiguracionFinanzasSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfiguracionFinanzas
        fields = [
            'id', 'nombre_iglesia', 'nombre_distrito', 'ciudad',
            'pres_distrital_pct', 'pres_educacional_pct',
            'pres_evangelismo_pct', 'jubilacion_monto',
            'actualizado_por', 'updated_at'
        ]
        read_only_fields = ['id', 'actualizado_por', 'updated_at']


class InformeMensualSerializer(serializers.ModelSerializer):
    generado_por_nombre = serializers.SerializerMethodField()

    class Meta:
        model = InformeMensual
        fields = [
            'id', 'anio', 'mes', 'datos', 'generado_por',
            'generado_por_nombre', 'fecha_generacion', 'updated_at'
        ]
        read_only_fields = ['generado_por_nombre', 'fecha_generacion', 'updated_at']

    def get_generado_por_nombre(self, obj):
        if obj.generado_por:
            return obj.generado_por.get_full_name() or obj.generado_por.username
        return None


class MovimientoTesoreriaSerializer(serializers.ModelSerializer):
    registrado_por_nombre = serializers.SerializerMethodField()

    class Meta:
        model = MovimientoTesoreria
        fields = [
            'id', 'tipo', 'monto', 'descripcion', 'fecha',
            'imagen', 'registrado_por', 'registrado_por_nombre', 'created_at'
        ]
        read_only_fields = ['registrado_por', 'registrado_por_nombre', 'created_at']

    def get_registrado_por_nombre(self, obj):
        if obj.registrado_por:
            return obj.registrado_por.get_full_name() or obj.registrado_por.username
        return None


class CuotaFijaSerializer(serializers.ModelSerializer):
    ministry_nombre = serializers.SerializerMethodField()
    ministry_slug = serializers.SerializerMethodField()

    class Meta:
        model = CuotaFija
        fields = ['id', 'ministry', 'ministry_nombre', 'ministry_slug', 'tipo', 'monto', 'updated_at']
        read_only_fields = ['ministry_nombre', 'ministry_slug', 'updated_at']

    def get_ministry_nombre(self, obj):
        return obj.ministry.nombre

    def get_ministry_slug(self, obj):
        return obj.ministry.slug
