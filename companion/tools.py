import random
from typing import List
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import tool

from companion.db.tasks import Task, query_tasks
from companion.db.utils import UserId


class SearchInput(BaseModel):
    query: str = Field(
        description='Should be a search query an empty string "" fetches all tasks',
        default="",
    )
    state: str = Field(
        description='Specify "pending" to only get pending tasks, "completed" to only get completed tasks, '
        'or "all" to get both pending and completed tasks',
        default="pending",
        regex="(all|pending|completed)",
    )


def human_readable_tasks(tasks: List[Task]) -> str:
    return "\n---\n".join([task.human_readable() for task in tasks])


def query_tasks_impl(user_id: UserId, query: str = None, state: str = None) -> str:
    if query is None:
        query = ""
    if state is None:
        state = "pending"
    tasks = query_tasks(user_id, query, state)

    if len(tasks) == 0:
        return (
            "No tasks found that match the search criterion. Consider using different search terms."
        )

    return f"""Found {len(tasks)} task/s that match the search criterion.
---
{human_readable_tasks(tasks)}
---
"""


def bind_query_tasks(user_id: UserId):
    @tool(args_schema=SearchInput)
    async def query_tasks(query: str = None, state: str = None) -> str:
        """Queries tasks of the given user based on the given criterion"""
        return query_tasks_impl(user_id, query, state)

    return query_tasks
