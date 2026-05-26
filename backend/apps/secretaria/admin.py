from django.contrib import admin
from apps.secretaria.models import (
    ActaReunion, SolicitudTramite, VisitaIglesia,
    ComunicadoInterno, LecturaComunicado, HistorialEstadoMiembro,
    ConfiguracionWhatsApp, MensajeWhatsApp, EnvioWhatsAppLog,
)

admin.site.register(ActaReunion)
admin.site.register(SolicitudTramite)
admin.site.register(VisitaIglesia)
admin.site.register(ComunicadoInterno)
admin.site.register(LecturaComunicado)
admin.site.register(HistorialEstadoMiembro)
admin.site.register(ConfiguracionWhatsApp)
admin.site.register(MensajeWhatsApp)
admin.site.register(EnvioWhatsAppLog)
