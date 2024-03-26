import json
from langchain.agents import AgentExecutor, create_openai_tools_agent, StructuredChatAgent
from langchain.agents.openai_functions_agent.agent_token_buffer_memory import (
    AgentTokenBufferMemory,
)
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain_openai import ChatOpenAI
from companion.tools import bind_query_tasks, get_items, where_cat_is_hiding
from langchain.memory import ConversationBufferMemory

AGENT_NAME = "Agent"


class Companion:
    def __init__(self, user_id: str) -> None:
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
        self.runnable = self.agent_executor.with_config(
            {"run_name": AGENT_NAME},
        )

    def stop_eventually(self):
        self.agent_executor.max_iterations = 0

    async def astream_events(self, user_input: str):
        async for event in self.runnable.astream_events(
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
