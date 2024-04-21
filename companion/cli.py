import asyncio
from datetime import datetime
import json
from companion.companion import Companion


async def display_frames(async_generator):
    tools = {}
    async for frame in async_generator:
        frame = frame  # type: str
        if frame.startswith("on_tool_start|"):
            tool = frame[len("on_tool_start|") :]
            tool = json.loads(tool)
            tools[tool["runId"]] = tool
        elif frame.startswith("on_tool_end|"):
            tool = frame[len("on_tool_end|") :]
            tool = json.loads(tool)
            tools[tool["runId"]] = {**tools[tool["runId"]], **tool}
        elif frame.startswith("|"):
            text = frame[1:]
            print(text, end="")

    print(f"\n---\nTools Used:")
    for tool in tools.values():
        output = tool["output"].replace("\n", "\n            ")
        print(
            f""" -- \n    Name: {tool['toolName']}
    Input: {json.dumps(tool['input'])}
    Output: {output}"""
        )


def multiline_input(prompt: str = ""):
    print(prompt, end="")
    contents = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        contents.append(line)
    return "\n".join(contents)


def exec_conversation(user_id: str):
    companion = Companion(user_id, datetime.now().astimezone().tzinfo.tzname(None))

    while True:
        user_input = multiline_input("User prompt (Ctrl-D or Ctrl-Z on windows to send): ")
        if user_input == None:
            break
        async_generator = companion.astream_events(user_input)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(display_frames(async_generator))

    print("Conversation concluded")


if __name__ == "__main__":
    import argparse
    import os
    import logging
    from dotenv import load_dotenv

    from companion.cli import exec_conversation

    load_dotenv(".env.local")
    load_dotenv(".env", override=True)

    # Read the log level from the environment variable (default to WARNING)
    log_level = os.environ.get("LOGLEVEL", "WARNING").upper()

    # Configure the logging module
    logging.basicConfig(level=log_level)

    parser = argparse.ArgumentParser(description="task-companion-cli")
    parser.add_argument("user_id", type=str, help="The user ID of the user eg. 9812352")

    args = parser.parse_args()

    exec_conversation(args.user_id)
