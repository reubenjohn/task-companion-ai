import asyncio
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


def exec_conversation(user_id: str):
    companion = Companion(user_id)

    while True:
        user_input = input("User prompt: ")
        if user_input == None:
            break
        async_generator = companion.astream_events(user_input)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(display_frames(async_generator))

    print("Conversation concluded")


if __name__ == "__main__":
    import argparse
    from dotenv import load_dotenv

    from companion.cli import exec_conversation

    load_dotenv(".env.local")
    load_dotenv(".env", override=True)

    parser = argparse.ArgumentParser(description="task-companion-cli")
    parser.add_argument("user_id", type=str, help="The user ID of the user eg. 9812352")

    args = parser.parse_args()

    exec_conversation(args.user_id)
