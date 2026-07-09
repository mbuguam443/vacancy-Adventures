#!/usr/bin/env sh
python manage.py migrate --noinput
exec gunicorn safari_tours.wsgi --log-file -