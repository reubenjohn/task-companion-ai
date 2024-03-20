import asyncio

from main.utils.generators import (
    sync_generator_from_async,
    wrap_generator_in_json_array,
)

from django.http import StreamingHttpResponse


async def get_stream():
    for i in range(100):
        yield i
        await asyncio.sleep(0.1)  # Non-blocking sleep


def stream(request, user_id):
    sync_gen = sync_generator_from_async(get_stream())
    sync_gen = wrap_generator_in_json_array(sync_gen)
    return StreamingHttpResponse(sync_gen, content_type="application/json")
