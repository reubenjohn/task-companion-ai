from dataclasses import dataclass
import json
import logging
from typing import List
from django.db import models
from .utils import UserId, redis
from fuzzywuzzy import fuzz

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
    priority: int

    def human_readable(self) -> str:
        title = self.title.replace("\n", " ")
        priority = self.priority
        result = f"""Title: {title}
State: {self.state}"""
        if self.state != "completed":
            result += f"\nPriority: {PRIORITY_LABELS[priority]}"
        return result


def get_tasks(user_id: UserId, limit: int = 10) -> List[Task]:
    task_list_key = f"user:tasklist:{user_id}:default"
    logging.info(f"User {user_id} fetching tasks from task list: {task_list_key}")
    tasks = [Task(**json.loads(task)) for task in redis.zrange(task_list_key, 0, limit)]
    logging.info(f"User {user_id} fetched {len(tasks)} tasks from list {task_list_key}")
    return tasks


def text_search_score(text: Task, query: str) -> float:
    return max(
        fuzz.ratio(text, query) + 0.3,  # Same order full match
        fuzz.partial_ratio(text, query) + 0.2,  # Same order partial match
        fuzz.token_sort_ratio(text, query) + 0.1,  # Any order full match
        fuzz.partial_token_sort_ratio(text, query),  # Any order partial match
    )


def task_search_score(task: Task, query: str) -> float:
    return text_search_score(task.title, query)


def query_tasks(user_id: UserId, query: str, state: str) -> List[Task]:
    tasks = get_tasks(user_id)
    if not query:
        return tasks

    scored_tasks = [
        (task_search_score(task, query), task)
        for task in tasks
        if not state or state == "all" or task.state == state
    ]
    scored_tasks = [(score, task) for score, task in scored_tasks if score > 50.0]
    scored_tasks.sort(key=lambda score_task: score_task[0], reverse=True)
    return [task for _, task in scored_tasks]


def delete_task(user_id: UserId, task_id: TaskId):
    task_list_key = f"user:tasklist:{user_id}:default"
    task_id = float(task_id)
    logging.info(f"Deleting task '{task_id}' from task list: {task_list_key}")
    result = redis.zremrangebyscore(task_list_key, task_id, task_id)
    logging.info(
        f"Deleting task '{task_id}' from task list: {task_list_key} resulted in {result}"
    )
    return result
