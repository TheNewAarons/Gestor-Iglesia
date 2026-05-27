#!/bin/bash
export DJANGO_SETTINGS_MODULE=config.settings.local
export PATH="/opt/homebrew/opt/postgresql@16/bin:$PATH"
cd "$(dirname "$0")/../backend"
source .venv/bin/activate
exec gunicorn config.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 3 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -
