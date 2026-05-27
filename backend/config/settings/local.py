from .base import *

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '192.168.1.85', '100.99.228.113']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

CORS_ALLOWED_ORIGINS = [
    'http://localhost:4321',
    'http://localhost:4322',
    'http://localhost:3000',
    'http://192.168.1.85:4321',
    'http://100.99.228.113:4321',
    'http://192.168.1.85:4322',
    'http://100.99.228.113:4322',
]

CSRF_TRUSTED_ORIGINS = [
    'http://localhost:4321',
    'http://localhost:4322',
    'http://localhost:3000',
    'http://192.168.1.85:4321',
    'http://100.99.228.113:4321',
    'http://192.168.1.85:4322',
    'http://100.99.228.113:4322',
]

CSRF_COOKIE_HTTPONLY = False

REST_FRAMEWORK = {
    **REST_FRAMEWORK,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '1000/day',
        'user': '10000/day',
    },
}
