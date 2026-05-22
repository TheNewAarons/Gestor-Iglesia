from rest_framework import serializers
from .models import ConfiguracionFinanzas, InformeMensual


class ConfiguracionFinanzasSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfiguracionFinanzas
        fields = [
            'id', 'pres_distrital_pct', 'pres_educacional_pct',
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
