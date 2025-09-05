#!/usr/bin/env bash

python manage.py collectstatic --noinput
python manage.py migrate --noinput
python -m gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 0 littlelemon.wsgi:application