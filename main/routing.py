from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"api/ws/sheet/(?P<sheet_name>\w+)/$", consumers.SheetConsumer.as_asgi()),
]
