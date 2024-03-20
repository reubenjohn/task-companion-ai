# import logging
# from django.http import JsonResponse

# from main.models.tasks import Task

# def tasks(request):
#     logging.debug("Fetching tasks")
#     top_tasks =Task.objects.all()[:100]
#     return JsonResponse({"tasks": list(top_tasks.values())})

# def create_task(request):
#     pass

import logging
from django.http import JsonResponse
from rest_framework.views import APIView

from main.models.tasks import query_tasks

from ..models import get_tasks


class TasksApiView(APIView):
    def get(self, request, user_id, *args, **kwargs):
        """
        List all the tasks for given requested user
        """
        query = self.request.GET.get("query", "")
        state = self.request.GET.get("state", "all")

        tasks = query_tasks(user_id, query, state)

        return JsonResponse({"tasks": tasks})
