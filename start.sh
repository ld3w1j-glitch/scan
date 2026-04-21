#!/usr/bin/env sh
set -eu

PORT_VALUE="${PORT:-8080}"
exec gunicorn app:app --bind "0.0.0.0:${PORT_VALUE}" --workers 2 --threads 4 --timeout 120
