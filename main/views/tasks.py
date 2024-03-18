# import logging
# from django.http import JsonResponse

# from main.models.tasks import Task

# def tasks(request):
#     logging.debug("Fetching tasks")
#     top_tasks =Task.objects.all()[:100]
#     return JsonResponse({"tasks": list(top_tasks.values())})

# def create_task(request):
#     pass

import json
import logging
import os
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from ..models import get_tasks


class TasksApiView(APIView):
    # add permission to check if user is authenticated
    permission_classes = [permissions.IsAuthenticated]

    # 1. List all
    def get(self, request, user_id, *args, **kwargs):
        '''
        List all the tasks for given requested user
        '''
        logging.info("Got tasks")
        tasks = get_tasks(user_id)
        return JsonResponse({"tasks": tasks})


    # 2. Create
    def post(self, request, user_id, *args, **kwargs):
        '''
        Create the Todo with given todo data
        '''
        # data = request.data
        # serializer = TodoSerializer(data=data)
        # if serializer.is_valid():
        #     serializer.save()
        #     return Response(serializer.data, status=status.HTTP_201_CREATED)

        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return JsonResponse({})
