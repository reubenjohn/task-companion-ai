import json
import logging
import os
from django.http import JsonResponse

from langchain.agents.openai_assistant import OpenAIAssistantRunnable


def get_assistant():
    try:
        assistant_id = os.getenv('OPENAI_ASSISTANT_ID')
        logging.info(f"assistant_id={assistant_id}")
        return OpenAIAssistantRunnable(
            assistant_id=assistant_id,
        )
    except Exception as e:
        logging.error(e)
        new_assistant = OpenAIAssistantRunnable.create_assistant(
                name="langchain assistant",
                instructions="You are a personal math tutor.",
                tools=[],
                model="gpt-3.5-turbo",
            )
        os.environ['OPENAI_ASSISTANT_ID'] = new_assistant.assistant_id
        return new_assistant
        

def assistant(request):
    logging.debug("Invoking assistant")
    interpretter_assistant = get_assistant()
    output = interpretter_assistant.invoke({"content": "What's 10 - 4 raised to the 2.7"})
    return JsonResponse({"messages": [json.loads(message.json()) for message in output]})