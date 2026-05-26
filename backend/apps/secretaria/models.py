from django.db import models


class ActaReunion(models.Model):
    titulo = models.CharField(max_length=200)

    class Meta:
        verbose_name = 'Acta de Reunión'
        verbose_name_plural = 'Actas de Reuniones'

    def __str__(self):
        return self.titulo


class SolicitudTramite(models.Model):
    titulo = models.CharField(max_length=200)

    class Meta:
        verbose_name = 'Solicitud de Trámite'
        verbose_name_plural = 'Solicitudes de Trámites'

    def __str__(self):
        return self.titulo


class VisitaIglesia(models.Model):
    nombre = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Visita de Iglesia'
        verbose_name_plural = 'Visitas de Iglesias'

    def __str__(self):
        return self.nombre


class ComunicadoInterno(models.Model):
    titulo = models.CharField(max_length=200)

    class Meta:
        verbose_name = 'Comunicado Interno'
        verbose_name_plural = 'Comunicados Internos'

    def __str__(self):
        return self.titulo


class LecturaComunicado(models.Model):
    comunicado_id = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Lectura de Comunicado'
        verbose_name_plural = 'Lecturas de Comunicados'


class HistorialEstadoMiembro(models.Model):
    miembro_id = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Historial Estado Miembro'
        verbose_name_plural = 'Historial Estados Miembros'


class ConfiguracionWhatsApp(models.Model):
    clave = models.CharField(max_length=100, default='')

    class Meta:
        verbose_name = 'Configuración WhatsApp'
        verbose_name_plural = 'Configuraciones WhatsApp'


class MensajeWhatsApp(models.Model):
    destinatario = models.CharField(max_length=100, default='')

    class Meta:
        verbose_name = 'Mensaje WhatsApp'
        verbose_name_plural = 'Mensajes WhatsApp'


class EnvioWhatsAppLog(models.Model):
    mensaje_id = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Log Envío WhatsApp'
        verbose_name_plural = 'Logs Envíos WhatsApp'
