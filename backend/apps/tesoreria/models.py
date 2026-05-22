from django.db import models
from django.conf import settings


class ConfiguracionFinanzas(models.Model):
    """Configuración de finanzas de la iglesia (singleton)."""
    pres_distrital_pct = models.DecimalField(
        max_digits=5, decimal_places=2, default=10.00,
        help_text='Porcentaje de PRES.DISTRITAL (ej: 10.00 = 10%)'
    )
    pres_educacional_pct = models.DecimalField(
        max_digits=5, decimal_places=2, default=3.00,
        help_text='Porcentaje de PRES EDUCACIONAL (ej: 3.00 = 3%)'
    )
    pres_evangelismo_pct = models.DecimalField(
        max_digits=5, decimal_places=2, default=2.00,
        help_text='Porcentaje de PRES.EVANGELISMO (ej: 2.00 = 2%)'
    )
    jubilacion_monto = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
        help_text='Monto fijo de jubilación mensual'
    )
    actualizado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Configuración de Finanzas'
        verbose_name_plural = 'Configuración de Finanzas'

    def __str__(self):
        return 'Configuración de Finanzas'

    @classmethod
    def obtener(cls):
        """Retorna la configuración existente o crea una con valores por defecto."""
        config, _ = cls.objects.get_or_create(pk=1)
        return config


class InformeMensual(models.Model):
    """Informe mensual consolidado de finanzas (snapshot)."""
    anio = models.IntegerField()
    mes = models.IntegerField()
    datos = models.JSONField(help_text='Estructura completa del informe mensual')
    generado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    fecha_generacion = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Informe Mensual'
        verbose_name_plural = 'Informes Mensuales'
        ordering = ['-anio', '-mes']
        unique_together = ['anio', 'mes']

    def __str__(self):
        return f'Informe {self.mes}/{self.anio}'
