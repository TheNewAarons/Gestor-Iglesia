from rest_framework.throttling import AnonRateThrottle


class LoginRateThrottle(AnonRateThrottle):
    """Máx 10 intentos de login por minuto por IP."""
    scope = 'login'
