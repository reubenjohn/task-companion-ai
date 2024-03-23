"""
URL configuration for containers_python_django project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include, re_path
from main.views import home, TasksApiView
from main.views.companion import chat
from main.views.companion.chat import ChatConsumer
from main.views.companion.tools import get_items, query_tasks, where_cat_is_hiding
from main.views.stream_demo import stream

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api-auth/", include("rest_framework.urls")),
    path("api", home),
    path("", home),
    path("api/tasks/<int:user_id>", TasksApiView.as_view()),
    path("api/companion/tools/get_items", get_items),
    path("api/companion/tools/where_cat_is_hiding", where_cat_is_hiding),
    path("api/companion/tools/query_tasks/<int:user_id>", query_tasks),
    path("api/stream/<int:user_id>", stream),
]

websocket_urlpatterns = [
    path("api/companion/chat/<int:user_id>", ChatConsumer.as_asgi()),
]
