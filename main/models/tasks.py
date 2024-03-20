from dataclasses import dataclass
import json
import logging
from typing import List
from django.db import models
from .utils import UserId, redis


TaskId = float


@dataclass
class NewTaskData:
    title: str
    priority: int


"""
class Task(models.Model):
    class State(models.TextChoices):
        pending = "pending", "pending"
        completed = "completed", "completed"

    class Priority(models.IntegerChoices):
        unknown = 0, "unknown"
        critical = 1, "critical"
        high = 2, "high"
        medium = 3, "medium"
        low = 4, "low"
        obsolete = 99, "obsolete"

    title = models.CharField(max_length=200)
    state = models.CharField(
        max_length=20, choices=State.choices, default=State.pending
    )
    priority = models.IntegerField(choices=Priority.choices, default=Priority.unknown)
"""

PRIORITY_LABELS = {
    0: "unknown",
    1: "critical",
    2: "high",
    3: "medium",
    4: "low",
    99: "obsolete",
}


@dataclass
class Task:
    id: float
    title: str
    state: str
    priority: str

    def human_readable(self) -> str:
        title = self.title.replace("\n", " ")
        priority = self.priority
        result = f"""Title: {title}
State: {self.state}"""
        if self.state != "completed":
            result += f"\nPriority: {PRIORITY_LABELS[priority]}"
        return result


def get_tasks(user_id: UserId) -> List[Task]:
    task_list_key = f"user:tasklist:{user_id}:default"
    logging.info(f"Fetching tasks from task list: {task_list_key}")
    return [
        Task(**json.loads(task)) for task in redis.zrange(task_list_key, -1e15, 1e15)
    ]


def query_tasks(user_id: UserId, query: str, state: str) -> List[Task]:
    tasks = get_tasks(user_id)
    return tasks


def delete_task(user_id: UserId, task_id: TaskId):
    task_list_key = f"user:tasklist:{user_id}:default"
    task_id = float(task_id)
    logging.info(f"Deleting task '{task_id}' from task list: {task_list_key}")
    result = redis.zremrangebyscore(task_list_key, task_id, task_id)
    logging.info(
        f"Deleting task '{task_id}' from task list: {task_list_key} resulted in {result}"
    )
    return result
