from django.urls import path
from main.views.companion.chat import ChatConsumer

websocket_urlpatterns = [
    path("api/companion/chat/<int:user_id>", ChatConsumer.as_asgi()),
]
