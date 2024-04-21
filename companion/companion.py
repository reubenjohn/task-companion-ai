import json
import time
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from companion.db.conversation_history import RedisConversationSummaryBufferMemory
from companion.db.feed import (
    events_to_messages,
    get_feed,
)
from companion.prompt import TASK_COMPANION_PROMPT
from companion.tools import bind_query_tasks

AGENT_NAME = "Agent"


class Companion:
    def __init__(
        self,
        user_id: str,
        timezone: str,
        max_message_size: int = 1000,
        max_token_limit: int = 2000,
    ) -> None:
        model = ChatOpenAI(temperature=0, streaming=True)
        memory = RedisConversationSummaryBufferMemory(
            user_id=user_id,
            memory_key="chat_history",
            llm=model,
            return_messages=True,
            output_key="output",
            max_token_limit=max_token_limit,
        )
        memory.fetch_from_db()
        messages = memory.chat_memory.messages

        last_message_timestamp = (
            messages[-1].additional_kwargs.get("creationUtcMillis", None)
            if len(messages) > 0
            else 0
        )
        if last_message_timestamp is not None:
            feed_since = get_feed(user_id, limit=20, start_time=last_message_timestamp + 1)
            memory.chat_memory.add_messages(events_to_messages(feed_since, timezone))

        self.max_message_size = max_message_size

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", TASK_COMPANION_PROMPT),
                MessagesPlaceholder("chat_history", optional=True),
                ("human", "{input}"),
                MessagesPlaceholder("agent_scratchpad"),
            ]
        )

        tools = [bind_query_tasks(user_id)]

        # agent = get_assistant(tools)
        agent = create_openai_tools_agent(model.with_config({"tags": ["agent_llm"]}), tools, prompt)

        self.agent_executor = AgentExecutor(
            agent=agent, tools=tools, memory=memory, return_intermediate_steps=True
        )
        self.runnable = self.agent_executor.with_config(
            {"run_name": AGENT_NAME},
        )

    def stop_eventually(self):
        self.agent_executor.max_iterations = 0

    async def astream_events(self, user_input: str, timezone: str):
        memory = self.agent_executor.memory  # type: RedisConversationSummaryBufferMemory
        memory_messages = memory.chat_memory.messages
        if len(memory_messages) > 0:
            last_message = memory_messages[-1]
            if last_message.type == "human" and last_message.content == user_input:
                memory_messages.pop()

        msg_creation_time_millis = time.time() * 1000

        if len(user_input) > self.max_message_size:
            raise Exception(
                f"User message of size {len(user_input)} exceeds limit of {self.max_message_size}"
            )

        yield f"message_time|{msg_creation_time_millis}"
        async for event in self.runnable.astream_events(
            {"input": user_input},
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
                    yield f"|{content}"
            elif kind == "on_tool_start":
                data = dict(
                    runId=event["run_id"], toolName=event_name, input=event["data"].get("input")
                )
                yield f"{kind}|{json.dumps(data)}"
            elif kind == "on_tool_end":
                data = dict(
                    runId=event["run_id"], toolName=event_name, output=event["data"].get("output")
                )
                yield f"{kind}|{json.dumps(data)}"

        memory_messages = memory.chat_memory.messages
        if len(memory_messages) > 0:
            memory_messages[-1].additional_kwargs["creationUtcMillis"] = msg_creation_time_millis

        memory.persist()
