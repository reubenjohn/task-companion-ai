from dataclasses import dataclass
import json
import logging
from typing import List
from pydantic import BaseModel
from .utils import UserId, redis
from fuzzywuzzy import fuzz

TaskId = float


@dataclass
class NewTaskData:
    title: str
    priority: int


PRIORITY_LABELS = {
    0: "unknown",
    1: "critical",
    2: "high",
    3: "medium",
    4: "low",
    99: "obsolete",
}


class Task(BaseModel):
    id: float
    title: str
    state: str
    priority: int

    def human_readable(self) -> str:
        title = self.title.replace("\n", " ")
        priority = self.priority
        result = f"""Title: {title}"""
        if self.state != "completed":
            result += f"\nState: {self.state}\nPriority: {PRIORITY_LABELS[priority]}"
        return result


def get_tasks(user_id: UserId, limit: int = 10) -> List[Task]:
    task_list_key = f"user:tasklist:{user_id}:default"
    logging.info(f"User {user_id} fetching tasks from task list: {task_list_key}")
    tasks = [Task(**json.loads(task)) for task in redis().zrange(task_list_key, 0, limit)]
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
    logging.info(f"query_tasks(user_id={user_id}, query={query}, state={state})")
    tasks = get_tasks(user_id)
    if state != "all":
        tasks = [task for task in tasks if state == task.state]
    if not query:
        return tasks

    scored_tasks = [(task_search_score(task, query), task) for task in tasks]
    scored_tasks = [(score, task) for score, task in scored_tasks if score > 50.0]
    scored_tasks.sort(key=lambda score_task: score_task[0], reverse=True)
    return [task for _, task in scored_tasks]


def delete_task(user_id: UserId, task_id: TaskId):
    task_list_key = f"user:tasklist:{user_id}:default"
    task_id = float(task_id)
    logging.info(f"Deleting task '{task_id}' from task list: {task_list_key}")
    result = redis().zremrangebyscore(task_list_key, task_id, task_id)
    logging.info(f"Deleting task '{task_id}' from task list: {task_list_key} resulted in {result}")
    return result
