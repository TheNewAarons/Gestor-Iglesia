from rest_framework.views import exception_handler
from rest_framework.response import Response


def custom_exception_handler(exc, context):
    """Handler estandarizado de errores JSON: {code, message, errors}"""
    response = exception_handler(exc, context)

    if response is not None:
        custom_response = {
            'code': _get_error_code(response.status_code, exc),
            'message': _get_error_message(exc, response),
        }

        if isinstance(response.data, dict):
            custom_response['errors'] = response.data
        elif isinstance(response.data, list):
            custom_response['errors'] = {'detail': response.data}
        else:
            custom_response['errors'] = {'detail': str(response.data)}

        response.data = custom_response

    return response


def _get_error_code(status_code, exc):
    codes = {
        400: 'validation_error',
        401: 'authentication_error',
        403: 'permission_denied',
        404: 'not_found',
        405: 'method_not_allowed',
        429: 'throttled',
        500: 'server_error',
    }
    return codes.get(status_code, 'error')


def _get_error_message(exc, response):
    default_messages = {
        400: 'Los datos proporcionados son inválidos.',
        401: 'No autenticado. Inicia sesión para continuar.',
        403: 'No tienes permiso para realizar esta acción.',
        404: 'El recurso solicitado no existe.',
        405: 'Método no permitido.',
        429: 'Demasiadas solicitudes. Intenta de nuevo más tarde.',
        500: 'Error interno del servidor.',
    }
    return default_messages.get(
        response.status_code,
        getattr(exc, 'default_detail', 'Ha ocurrido un error.')
    )
