 # Sample Django Project for Back4app Containers
 
 This repository contains a sample Django application designed to be deployed on Back4app Containers. It serves as a template and guide to help you get started with deploying your own Django applications on Back4app Containers.
 
 ## Project Structure
 
 ```
 ├── Dockerfile # Dockerfile for building the Docker image 
 ├── manage.py # Django's command-line utility for administrative tasks
 ├── myapp # Your Django application
 │   ├── __init__.py
 │   ├── settings.py
 │   ├── urls.py
 │   └── wsgi.py
 ├── templates # HTML templates
 │   └── home.html
 └── requirements.txt # Python dependencies for the Django application
 ```
 
 ## Getting Started
 
 1. Clone this repository to your local machine.
 
 ```bash
 git clone https://github.com/templates-back4app/containers-python-django.git
 cd containers-python-django
 ```
 
 2. Install the required dependencies using pip.
 
 ```bash
 pip install -r requirements.txt
 ```
 
 3. Run the Django application locally.
 
 ```bash
 python manage.py runserver
 ```
 
 Your Django application should now be running locally at http://127.0.0.1:8000/.
 
 ## Deploying to Back4app Containers 
 
 Follow the step-by-step guide in the article "Run a Django Container App"(https://www.back4app.com/docs-containers/run-a-django-container-app) to deploy this sample Django application on Back4app Containers.
 
 ## Customizing the Template 
 
 Feel free to customize this template by modifying the `myapp` directory and adding your own routes, views, and functionality. Make sure to update the requirements.txt file with any additional dependencies your application requires.
 
 ## License 
 
 This sample Django project is released under the MIT License.
