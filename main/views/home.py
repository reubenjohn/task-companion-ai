from django.shortcuts import render


import logging


def home(request):
    logging.debug("Rendering home.html")
    return render(request, 'home.html')