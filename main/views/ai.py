import asyncio
import json
import logging
import os
import queue
import random
from threading import Thread
from django.http import StreamingHttpResponse

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.agents.openai_assistant import OpenAIAssistantRunnable
from langchain.tools import tool
from langchain_openai import ChatOpenAI


def get_assistant(tools):
    try:
        assistant_id = os.getenv("OPENAI_ASSISTANT_ID")
        logging.info(f"assistant_id={assistant_id}")
        return OpenAIAssistantRunnable(
            assistant_id=assistant_id,
        )
    except Exception as e:
        logging.error(e)
        new_assistant = OpenAIAssistantRunnable.create_assistant(
            name="langchain assistant",
            instructions="You are a personal math tutor.",
            tools=tools,
            model="gpt-3.5-turbo",
        )
        os.environ["OPENAI_ASSISTANT_ID"] = new_assistant.assistant_id
        return new_assistant


def assistant(request, user_id):
    generator = sync_generator_from_async(async_assistant(user_id))
    generator = wrap_generator_in_json_array(generator)
    return StreamingHttpResponse(
        generator,
        content_type="application/json",
    )


@tool
async def get_items(place: str) -> str:
    """Use this tool to look up which items are in the given place."""
    if "bed" in place:  # For under the bed
        return "socks, shoes and dust bunnies"
    if "shelf" in place:  # For 'shelf'
        return "books, penciles and pictures"
    else:  # if the agent decides to ask about a different place
        return "cat snacks"


@tool
async def where_cat_is_hiding() -> str:
    """Where is the cat hiding right now?"""
    return random.choice(["under the bed", "on the shelf"])


async def async_assistant(user_id):
    logging.debug("Invoking assistant")

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


async def get_stream():
    for i in range(100):
        yield i
        await asyncio.sleep(0.1)  # Non-blocking sleep


def async_generator_wrapper(async_gen, q):
    """
    Run the asynchronous generator and put each item into the queue.
    """

    async def run():
        async for item in async_gen:
            q.put(item)
        q.put(None)  # Sentinel to indicate the end of the stream

    asyncio.run(run())


def sync_generator_from_async(async_gen):
    q = queue.Queue()

    # Start the asynchronous generator in a separate thread
    Thread(target=async_generator_wrapper, args=(async_gen, q), daemon=True).start()

    def generator():
        """
        Synchronously yield items from the queue filled by the async generator.
        """
        while True:
            item = q.get()
            if item is None:  # Check for the end of the stream
                break
            yield item

    return generator()


def wrap_generator_in_json_array(sync_gen):
    yield "["
    first = True
    for elem in sync_gen:
        if not first:
            yield ","
        yield elem
        first = False
    yield "]"


def stream(request, user_id):
    sync_gen = sync_generator_from_async(get_stream())
    sync_gen = wrap_generator_in_json_array(sync_gen)
    return StreamingHttpResponse(sync_gen, content_type="application/json")
