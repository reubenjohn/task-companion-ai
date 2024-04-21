import logging
from typing import Any, Dict, List, Literal, Union
from pydantic import BaseModel, ConfigDict, TypeAdapter
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage

from companion.db.tasks import Task
from companion.db.utils import UserId, redis
from companion.utils import datetime_from_utc_to_local


EVENT_TYPE_CREATE_TASK = "create-task"
EVENT_TYPE_DELETE_TASK = "delete-task"
EVENT_TYPE_UPDATE_TASK = "update-task"
EVENT_TYPE_MESSAGE = "message"


EventTypeLiteral = Literal["create-task", "delete-task", "update-task", "message"]


class EventBase(BaseModel):
    type: EventTypeLiteral
    creationUtcMillis: float


class TaskEventBase(EventBase):
    task: Task


class CreateTaskEvent(TaskEventBase):
    type: Literal["create-task"]


class DeleteTaskEvent(TaskEventBase):
    type: Literal["delete-task"]


class UpdateTaskEvent(TaskEventBase):
    type: Literal["update-task"]
    previousValues: Dict[str, Any]


MESSAGE_ROLE_SYSTEM = "system"
MESSAGE_ROLE_USER = "user"
MESSAGE_ROLE_ASSISTANT = "assistant"


MessageRoleLiteral = Literal["system", "user", "assistant"]


class MessageEvent(EventBase, use_enum_values=True):
    type: Literal["message"]
    role: MessageRoleLiteral
    content: str


Event = Union[CreateTaskEvent | DeleteTaskEvent | UpdateTaskEvent | MessageEvent]
EventTypeAdapter = TypeAdapter(Event, config=ConfigDict(discriminator="type"))


def get_feed(user_id: UserId, limit: int = 10, start_time: float = None) -> List[Event]:
    feed_key = f"user:feed:{user_id}:default"
    logging.info(f"User {user_id} fetching events from feed: {feed_key}")

    results = (
        redis().zrange(feed_key, 0, limit)
        if start_time is None
        else redis().zrange(feed_key, start_time, 1e18, sortby="BYSCORE", offset=0, count=limit)
    )
    events = [
        EventTypeAdapter.validate_json(event_json) for event_json in results
    ]  # type: List[Event]
    logging.info(f"User {user_id} fetched {len(events)} events from feed: {feed_key}")

    return events


def event_to_message(event: Event, timezone: str) -> BaseMessage:
    creation_time = datetime_from_utc_to_local(event.creationUtcMillis, timezone)
    if event.type == "create-task":
        return SystemMessage(
            content=f"A new task was created at {creation_time}:\n{event.task.human_readable()}"
        )
    elif event.type == "delete-task":
        return SystemMessage(
            content=f"A task was deleted at {creation_time}:\n{event.task.human_readable()}"
        )
    elif event.type == "update-task":
        modifications = "\n".join(
            [
                f"{key} was changed from '{value}' to '{getattr(event.task, key, '<None>')}'"
                for key, value in event.previousValues.items()
            ]
        )
        return SystemMessage(
            content=f"""A task was modified at {creation_time}. The modifications are:
{modifications}
The resulting task is:
{event.task.human_readable()}"""
        )
    elif event.type == "message":
        if event.role == "system":
            return SystemMessage(content=event.content)
        elif event.role == "user":
            return HumanMessage(content=event.content)
        elif event.role == "assistant":
            return AIMessage(content=event.content)
        else:
            raise Exception(f"Unsupported event message role: {event.role}")
    else:
        raise NotImplementedError("Message type to human readible not yet implemented")


def events_to_messages(events: List[Event], timezone: str) -> List[BaseMessage]:
    return [event_to_message(event, timezone) for event in events]
