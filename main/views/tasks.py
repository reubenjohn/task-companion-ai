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
import os
from upstash_redis import Redis
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from ..models import Task
from ..serializers import TodoSerializer


redis = Redis(
    url=os.environ["KV_REST_API_URL"],
    token=os.environ["KV_REST_API_TOKEN"],
    )

class TasksApiView(APIView):
    # add permission to check if user is authenticated
    permission_classes = [permissions.IsAuthenticated]

    # 1. List all
    def get(self, request, *args, **kwargs):
        '''
        List all the todo items for given requested user
        '''
        todos = Task.objects
        serializer = TodoSerializer(todos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


    # 2. Create
    def post(self, request, *args, **kwargs):
        '''
        Create the Todo with given todo data
        '''
        data = request.data
        serializer = TodoSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def get_tasks(request, user_id):
    task_list_key = f'user:tasklist:{user_id}:default'
    logging.info(f"Fetching tasks from task list: {task_list_key}")
    return JsonResponse({"tasks": redis.zrange(task_list_key, 0, 100)})
