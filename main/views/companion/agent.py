from langchain.agents.openai_assistant import OpenAIAssistantRunnable


import logging
import os


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
