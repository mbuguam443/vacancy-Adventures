#!/bin/bash
python manage.py migrate --noinput
gunicorn safari_tours.wsgi --log-file -