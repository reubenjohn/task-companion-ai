# syntax=docker/dockerfile:1
FROM python:3.10-bullseye

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 8000

RUN chmod +x containers_python_django/startup.sh
RUN python manage.py makemigrations
RUN python manage.py migrate

CMD [ "./containers_python_django/startup.sh" ]
