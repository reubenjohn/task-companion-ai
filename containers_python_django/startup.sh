#!/bin/bash

python manage.py createsuperuser --noinput
python manage.py migrate
daphne containers_python_django.asgi:application --bind 0.0.0.0 -p 8000
