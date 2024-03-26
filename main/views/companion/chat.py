import asyncio
import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from companion.db.utils import UserId


from companion.companion import Companion


class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_id = None
        self.agent_executor = None
        self.companion = None  # type: Companion
        self.respond_task = None

    async def connect(self):
        self.user_id = UserId(self.scope["url_route"]["kwargs"]["user_id"])
        logging.info(f"User {self.user_id} opened chat websocket")

        await self.accept()

    async def disconnect(self, close_code):
        logging.info(f"User '{self.user_id}' disconnected chat websocket ({close_code})")
        await self.stop()

    async def stop(self):
        logging.info(f"User {self.user_id} stopping response")
        if self.companion:
            self.companion.stop_eventually()
        if self.respond_task:
            await self.respond_task

    async def receive(self, text_data: str):
        try:
            json_data = json.loads(text_data)
            cmd = json_data["command"]
            if cmd == "close":
                logging.info(f"User {self.user_id} requested websocket close")
                await self.close()  # Triggers self.disconnect(...)
            elif cmd == "respond":
                user_input = json_data["payload"]
                self.respond_task = asyncio.create_task(self.respond_to_user(user_input))
        except Exception as e:
            logging.error(e)
            await self.send(f"\nAn Error occurred: {str(e)}")

    async def respond_to_user(self, user_input: str):
        self.companion = Companion(self.user_id)
        async for frame in self.companion.astream_events(user_input):
            await self.send(frame)
        await self.close()
