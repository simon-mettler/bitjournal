#!/bin/sh
set -e

export DB_WAIT_TIMEOUT="${DB_WAIT_TIMEOUT:-60}"

echo "Waiting for database (timeout ${DB_WAIT_TIMEOUT}s)..."
python - <<EOF
import os, sys, time

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection

deadline = time.monotonic() + int(os.environ['DB_WAIT_TIMEOUT'])
while True:
    try:
        connection.ensure_connection()
        break
    except Exception as exc:
        if time.monotonic() > deadline:
            sys.exit(f'Database not reachable: {exc}')
        time.sleep(1)
EOF

echo "Applying migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting gunicorn..."
exec gunicorn config.wsgi:application \
    --bind "${GUNICORN_BIND:-0.0.0.0:8000}" \
    --workers "${WEB_CONCURRENCY:-3}" \
    --access-logfile - \
    "$@"
