from .base import *

DEBUG = False

ALLOWED_HOSTS = ['testserver']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

CORS_ALLOWED_ORIGINS = [
    'http://localhost:4321',
]

CSRF_TRUSTED_ORIGINS = [
    'http://localhost:4321',
]

CSRF_COOKIE_HTTPONLY = False

REST_FRAMEWORK = {
    **REST_FRAMEWORK,
    'DEFAULT_THROTTLE_CLASSES': [],
}

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]
