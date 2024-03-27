from django.http import HttpResponse


def health_check(request) -> str:
    return HttpResponse("Ok", content_type="text/plain")
