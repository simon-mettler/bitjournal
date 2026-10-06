"""Container healthcheck: GET /api/health/ with a Host header Django will accept."""

import os
import sys
import urllib.request

port = os.getenv('GUNICORN_BIND', '0.0.0.0:8000').rsplit(':', 1)[-1]
hosts = [h.strip() for h in os.getenv('ALLOWED_HOSTS', '').split(',') if h.strip()]
host = next((h for h in hosts if h != '*' and not h.startswith('.')), 'localhost')

request = urllib.request.Request(f'http://127.0.0.1:{port}/api/health/', headers={'Host': host})
try:
    with urllib.request.urlopen(request, timeout=4) as response:
        sys.exit(0 if response.status == 200 else 1)
except Exception:
    sys.exit(1)
