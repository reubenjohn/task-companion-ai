from dataclasses import dataclass
import json
import logging
from typing import List
from django.db import models
from .utils import redis

@dataclass
class NewTaskData:
    title: str
    priority: int

class Task(models.Model):
    class State(models.TextChoices):
        pending='pending', 'pending'
        completed='completed', 'completed'

    class Priority(models.IntegerChoices):
        unknown = 0, "unknown"
        critical = 1, "critical"
        high = 2, "high"
        medium = 3, "medium"
        low = 4, "low"
        obsolete = 99, "obsolete"

    title = models.CharField(max_length=200)
    state = models.CharField(max_length=20, choices=State.choices, default=State.pending)
    priority = models.IntegerField(choices=Priority.choices, default=Priority.unknown)


def get_tasks(user_id) -> List[dict]:
    task_list_key = f'user:tasklist:{user_id}:default2'
    logging.info(f"Fetching tasks from task list: {task_list_key}")
    return [json.loads(task) for task in redis.zrange(task_list_key, 0, 100)]

def delete_task(user_id, task_id):
    task_list_key = f'user:tasklist:{user_id}:default2'
    task_id = float(task_id)
    logging.info(f"Deleting task '{task_id}' from task list: {task_list_key}")
    result = redis.zremrangebyscore(task_list_key, task_id, task_id)
    logging.info(f"Deleting task '{task_id}' from task list: {task_list_key} resulted in {result}")
    return result
