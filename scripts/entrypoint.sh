#!/usr/bin/env bash

set -e

RUN_MANAGE_PY='poetry run python -m IAS.manage'

echo 'Collecting static files...'
$RUN_MANAGE_PY collectstatic --no-input

echo 'Running migrations...'
$RUN_MANAGE_PY migrate --no-input

# For django channels
# exec poetry run daphne IAS.ias.asgi:application -p 8000 -b 0.0.0.0

exec poetry run gunicorn IAS.ias.wsgi:application -p 8000 -b 0.0.0.0 --access-logfile - --error-logfile - --timeout 120 --workers 3
