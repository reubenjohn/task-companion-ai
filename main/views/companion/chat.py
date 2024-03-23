import asyncio
from dataclasses import dataclass
import json
import logging
from time import sleep
from channels.generic.websocket import AsyncWebsocketConsumer
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from main.models.utils import UserId
from main.utils.generators import (
    sync_generator_from_async,
    wrap_generator_in_json_array,
)


from django.http import HttpResponse, StreamingHttpResponse

from main.utils.json_encoder import StrJSONEncoder
from main.utils.tools import (
    bind_query_tasks,
    get_items,
    where_cat_is_hiding,
)


AGENT_NAME = "Agent"


class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_id = None
        self.agent_executor = None
        self.respond_task = None

    async def connect(self):
        self.user_id = UserId(self.scope["url_route"]["kwargs"]["user_id"])
        logging.info(f"User {self.user_id} opened chat websocket")

        await self.accept()

    async def disconnect(self, close_code):
        logging.info(f"User '{self.user_id}' disconnected chat websocket ({close_code})")
        await self.stop()

    async def stop(self):
        logging.info(f"User {self.user_id} stopping response")
        if self.agent_executor:
            self.agent_executor.max_iterations = 0
        if self.respond_task:
            await self.respond_task

    async def receive(self, text_data: str):
        try:
            json_data = json.loads(text_data)
            cmd = json_data["command"]
            if cmd == "close":
                logging.info(f"User {self.user_id} requested websocket close")
                await self.close()  # Triggers self.disconnect(...)
            elif cmd == "respond":
                user_input = json_data["payload"]
                self.respond_task = asyncio.create_task(self.respond_to_user(self.user_id, user_input))
        except Exception as e:
            logging.error(e)
            await self.send(f"\nAn Error occurred: {str(e)}")

    async def respond_to_user(self, user_id: UserId, user_input: str):
        model = ChatOpenAI(temperature=0, streaming=True)

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "You are a helpful assistant"),
                MessagesPlaceholder("chat_history", optional=True),
                ("human", "{input}"),
                MessagesPlaceholder("agent_scratchpad"),
            ]
        )

        tools = [bind_query_tasks(user_id), get_items, where_cat_is_hiding]

        # agent = get_assistant(tools)
        agent = create_openai_tools_agent(model.with_config({"tags": ["agent_llm"]}), tools, prompt)
        self.agent_executor = AgentExecutor(agent=agent, tools=tools)
        runnable = self.agent_executor.with_config(
            {"run_name": AGENT_NAME},
        )

        async for event in runnable.astream_events(
            {
                "input": user_input,
            },
            version="v1",
        ):
            kind = event["event"]
            event_name = event["name"]

            if self.agent_executor.max_iterations == 0:
                break
            # if event_name == AGENT_NAME and kind == "on_chain_start": # event['data'].get('input')
            if event_name == AGENT_NAME and kind == "on_chain_end":
                break  # Agent execution completed

            if kind == "on_chat_model_stream":
                content = event["data"]["chunk"].content
                if content:
                    # Empty content in the context of OpenAI means
                    # that the model is asking for a tool to be invoked.
                    # So we only print non-empty content
                    await self.send(f"|{content}")
            elif kind == "on_tool_start":
                data = dict(toolName=event_name, input=event["data"].get("input"))
                await self.send(f"{kind}|{json.dumps(data)}")
            elif kind == "on_tool_end":
                data = dict(toolName=event_name, output=event["data"].get("output"))
                await self.send(f"{kind}|{json.dumps(data)}")
