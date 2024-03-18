from rest_framework import serializers
from ..models.tasks import Task

class TodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["title", "state", "priority"]
