from django.db import models
from django.conf import settings
from apps.ministerios.models import Ministerio


class ConfiguracionFinanzas(models.Model):
    """Configuracion de finanzas de la iglesia (singleton)."""
    nombre_iglesia = models.CharField(
        max_length=200, default='Iglesia del Nazareno "Juan Noe"',
        help_text='Nombre de la iglesia para los informes'
    )
    nombre_distrito = models.CharField(
        max_length=200, default='Distrito Norte de Chile',
        help_text='Nombre del distrito para los informes'
    )
    ciudad = models.CharField(
        max_length=100, default='ARICA',
        help_text='Ciudad de la iglesia'
    )
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
        help_text='Monto fijo de jubilacion mensual'
    )
    actualizado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Configuracion de Finanzas'
        verbose_name_plural = 'Configuracion de Finanzas'

    def __str__(self):
        return 'Configuracion de Finanzas'

    @classmethod
    def obtener(cls):
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


class MovimientoTesoreria(models.Model):
    """Movimientos directos de tesoreria (no atados a un ministerio)."""
    TIPOS = [
        ('ingreso_diezmo', 'Diezmo'),
        ('ingreso_especial', 'Donacion Especial'),
        ('ingreso_ofrenda', 'Ofrenda'),
        ('ingreso_ahorro', 'Ahorro'),
        ('ingreso_proyectos', 'Proyectos'),
        ('egreso_sosten_pastoral', 'Sosten Pastoral'),
        ('egreso_beneficios_pastorales', 'Beneficios Pastorales'),
        ('egreso_varios_iglesia', 'Gastos Varios Iglesia'),
        ('egreso_fondo_contingencia', 'Fondo de Contingencia'),
    ]

    tipo = models.CharField(max_length=35, choices=TIPOS)
    ministry = models.ForeignKey(Ministerio, on_delete=models.SET_NULL, null=True, blank=True, related_name='movimientos_tesoreria')
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    descripcion = models.TextField(blank=True)
    fecha = models.DateField()
    imagen = models.ImageField(upload_to='tesoreria/', blank=True, null=True)
    registrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Movimiento de Tesoreria'
        verbose_name_plural = 'Movimientos de Tesoreria'
        ordering = ['-fecha']

    def __str__(self):
        return f'{self.get_tipo_display()} - {self.monto}'


class HistorialLog(models.Model):
    """Registro de auditoría de acciones sobre movimientos financieros."""
    ACCIONES = [
        ('creado', 'Creado'),
        ('editado', 'Editado'),
        ('eliminado', 'Eliminado'),
    ]

    entidad_tipo = models.CharField(max_length=20)  # 'ofrenda', 'movimiento_caja'
    entidad_id = models.IntegerField()
    accion = models.CharField(max_length=20, choices=ACCIONES)
    resumen = models.CharField(max_length=300, blank=True, help_text='Resumen legible de la acción')
    ministry = models.ForeignKey(Ministerio, on_delete=models.SET_NULL, null=True, blank=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Registro de auditoría'
        verbose_name_plural = 'Registros de auditoría'
        ordering = ['-fecha']

    def __str__(self):
        return f'{self.get_accion_display()} {self.entidad_tipo}#{self.entidad_id} — {self.resumen}'


class CuotaFija(models.Model):
    """Cuotas fijas mensuales de ministerios principales (COCE, cuota distrital)."""
    TIPOS = [
        ('coce', 'COCE'),
        ('cuota_distrital', 'Cuota Distrital'),
    ]

    ministry = models.ForeignKey(Ministerio, on_delete=models.CASCADE, related_name='cuotas_fijas')
    tipo = models.CharField(max_length=20, choices=TIPOS)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Cuota Fija'
        verbose_name_plural = 'Cuotas Fijas'
        unique_together = ['ministry', 'tipo']

    def __str__(self):
        return f'{self.get_tipo_display()} - {self.ministry.nombre}'
