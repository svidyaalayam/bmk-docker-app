#!/bin/sh
set -e

echo "Waiting for database..."
python <<'PY'
import os
import time

host = os.environ.get("POSTGRES_HOST")
if not host and not os.environ.get("DATABASE_URL", "").startswith("postgres"):
    raise SystemExit(0)

import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bmk_api_project.settings")
django.setup()

from django.db import connection

for attempt in range(30):
    try:
        connection.ensure_connection()
        print("Database is ready.")
        break
    except Exception as exc:
        print(f"DB not ready ({attempt + 1}/30): {exc}")
        time.sleep(2)
else:
    raise SystemExit("Database did not become ready in time.")
PY

python manage.py migrate --noinput
python manage.py collectstatic --noinput

if [ "${SEED_ON_START:-true}" = "true" ]; then
  python manage.py seed_schools
fi

exec gunicorn bmk_api_project.wsgi:application \
  --bind "0.0.0.0:${PORT:-8000}" \
  --workers "${GUNICORN_WORKERS:-3}" \
  --timeout "${GUNICORN_TIMEOUT:-60}"
