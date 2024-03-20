import json
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from main.utils.generators import (
    sync_generator_from_async,
    wrap_generator_in_json_array,
)


from django.http import StreamingHttpResponse

from main.utils.tools import get_items, where_cat_is_hiding


async def async_assistant(user_id):
    model = ChatOpenAI(temperature=0, streaming=True)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a helpful assistant"),
            MessagesPlaceholder("chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder("agent_scratchpad"),
        ]
    )

    agent_name = "Agent"

    tools = [get_items, where_cat_is_hiding]

    # agent = get_assistant(tools)
    agent = create_openai_tools_agent(
        model.with_config({"tags": ["agent_llm"]}), tools, prompt
    )
    agent_executor = AgentExecutor(agent=agent, tools=tools).with_config(
        {"run_name": agent_name},
    )

    # async for chunk in agent_executor.astream_log(
    #     {"input": "where is the cat hiding? what items are in that location?"},
    # ):
    #     print(chunk)

    async for event in agent_executor.astream_events(
        {"input": "where is the cat hiding? what items are in that location?"},
        version="v1",
    ):
        yield json.dumps(str(event))
        kind = event["event"]
        if kind == "on_chain_start":
            if event["name"] == agent_name:
                print(
                    f"Starting agent: {event['name']} with input: {event['data'].get('input')}"
                )
        elif kind == "on_chain_end":
            if event["name"] == agent_name:
                print()
                print("--")
                print(
                    f"Done agent: {event['name']} with output: {event['data'].get('output')['output']}"
                )
                return
        elif kind == "on_chat_model_stream":
            content = event["data"]["chunk"].content
            if content:
                # Empty content in the context of OpenAI means
                # that the model is asking for a tool to be invoked.
                # So we only print non-empty content
                print(content, end="|")
        elif kind == "on_tool_start":
            print("--")
            print(
                f"Starting tool: {event['name']} with inputs: {event['data'].get('input')}"
            )
        elif kind == "on_tool_end":
            print(f"Done tool: {event['name']}")
            print(f"Tool output was: {event['data'].get('output')}")
            print("--")


def chat(request, user_id):
    generator = sync_generator_from_async(async_assistant(user_id))
    generator = wrap_generator_in_json_array(generator)
    return StreamingHttpResponse(
        generator,
        content_type="application/json",
    )
