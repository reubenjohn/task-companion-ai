import random
from typing import List
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import tool

from main import models
from main.models.tasks import Task
from main.models.utils import UserId


def get_items_impl(place: str) -> str:
    if "bed" in place:  # For under the bed
        return "socks, shoes and dust bunnies"
    if "shelf" in place:  # For 'shelf'
        return "books, penciles and pictures"
    else:  # if the agent decides to ask about a different place
        return "cat snacks"


@tool
async def get_items(place: str) -> str:
    """Use this tool to look up which items are in the given place."""
    return get_items_impl(place)


def where_cat_is_hiding_impl() -> str:
    return random.choice(["under the bed", "on the shelf"])


@tool
async def where_cat_is_hiding() -> str:
    """Where is the cat hiding right now?"""
    return where_cat_is_hiding_impl()


class SearchInput(BaseModel):
    query: str = Field(
        description='Should be a search query an empty string "" fetches all tasks',
        default="",
    )
    state: str = Field(
        description='Specify "pending" to only get pending tasks, "completed" to only get completed tasks, '
        'or "all" to get both pending and completed tasks',
        default="all",
        regex="(all|pending|completed)",
    )


def human_readable_tasks(tasks: List[Task]) -> str:
    return "\n---\n".join([task.human_readable() for task in tasks])


def query_tasks_impl(user_id: UserId, query: str = None, state: str = None) -> str:
    if query is None:
        query = ""
    if state is None:
        state = "all"
    tasks = models.query_tasks(user_id, query, state)

    if len(tasks) == 0:
        return "No tasks found that match the search criterion. Consider using different search terms."

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
