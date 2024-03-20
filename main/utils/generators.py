import asyncio
import queue
from threading import Thread


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
