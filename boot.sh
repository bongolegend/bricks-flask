#!/bin/sh
. venv/bin/activate

#run migrations
python manage.py db upgrade

# run app
exec gunicorn -b :8000 main:app
