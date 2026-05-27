import base64
import requests
from django.conf import settings
from django.db import transaction

WA_SERVICE_URL = getattr(settings, 'WHATSAPP_SERVICE_URL', 'http://127.0.0.1:3001')


def _call(method: str, path: str, **kwargs):
    url = f'{WA_SERVICE_URL}{path}'
    try:
        resp = getattr(requests, method)(url, **kwargs)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        raise ConnectionError('Microservicio WhatsApp no disponible. Inicia whatsapp-service.')


def get_status() -> dict:
    return _call('get', '/status', timeout=3)


def get_qr() -> dict:
    return _call('get', '/qr', timeout=5)


def logout() -> dict:
    return _call('delete', '/logout', timeout=5)


def enviar_mensaje(grupo_jid: str, texto: str, imagen_path: str = None) -> None:
    payload = {'groupJid': grupo_jid, 'text': texto}
    if imagen_path:
        with open(imagen_path, 'rb') as f:
            payload['imageBase64'] = base64.b64encode(f.read()).decode()
    _call('post', '/send', json=payload, timeout=30)


@transaction.atomic
def ejecutar_envio_dominical(force: bool = False):
    from apps.secretaria.models import ConfiguracionWhatsApp, MensajeWhatsApp, EnvioWhatsAppLog

    config = ConfiguracionWhatsApp.obtener()
    if not config.grupo_jid:
        return None, 'sin_grupo'
    if not force and not config.activo:
        return None, 'inactivo'

    mensajes = MensajeWhatsApp.objects.filter(activo=True).order_by('numero')
    if not mensajes.exists():
        return None, 'sin_mensajes'

    idx = config.rotacion_index % mensajes.count()
    mensaje = list(mensajes)[idx]

    imagen_path = mensaje.imagen.path if mensaje.imagen else None
    estado = 'exitoso'
    error_detalle = ''

    try:
        enviar_mensaje(config.grupo_jid, mensaje.texto, imagen_path)
    except Exception as e:
        estado = 'fallido'
        error_detalle = str(e)

    log = EnvioWhatsAppLog.objects.create(
        mensaje=mensaje,
        texto_enviado=mensaje.texto,
        grupo_jid=config.grupo_jid,
        estado=estado,
        error_detalle=error_detalle,
    )

    if estado == 'exitoso':
        ConfiguracionWhatsApp.objects.filter(id=1).update(rotacion_index=idx + 1)

    return log, None
