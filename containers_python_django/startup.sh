#!/bin/bash

# Gets the details from the environment variables (see .env.example)
python manage.py createsuperuser --noinput
# Execute createsuperuser transaction on database along with any other pending migrations
python manage.py makemigrations
python manage.py migrate

daphne containers_python_django.asgi:application --bind 0.0.0.0 -p 8000
