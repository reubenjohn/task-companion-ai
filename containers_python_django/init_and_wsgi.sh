#!/bin/bash

python manage.py createsuperuser --noinput
gunicorn containers_python_django.wsgi:application --bind 0.0.0.0:8000
