#!/bin/sh

sleep 5
python manage.py migrate --noinput

# Сбор статических файлов
python manage.py collectstatic --noinput --clear

gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers=7