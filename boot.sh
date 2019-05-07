#!/bin/sh
. venv/bin/activate
# flask db upgrade
# flask translate compile
exec gunicorn -b :8000 main:app
