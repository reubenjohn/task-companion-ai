import json
import logging
from time import sleep
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


class SheetConsumer(WebsocketConsumer):
    def connect(self):
        logging.info("Websocket connection openned")
        self.sheet_name = self.scope["url_route"]["kwargs"]["sheet_name"]
        self.sheet_group_name = "sheet_%s" % self.sheet_name

        self.accept()

        for i in range(100):
            self.send(text_data=f"{i} ")
            sleep(0.1)
        self.close()

    def disconnect(self, close_code):
        logging.info("Websocket connection closed")

    # Receive message from WebSocket
    def receive(self, text_data):
        self.send(text_data=text_data)

    # Receive message from sheet group
    def refresh_sheet(self, event):
        # Send sheet_name to WebSocket
        self.send(
            text_data=json.dumps(
                {
                    "sheet_name": event["sheet_name"],
                    "object_id": event["object_id"],
                    "column_index": event["column_index"],
                    "new_value": event["new_value"],
                    "broadcaster_id": event["broadcaster_id"],
                }
            )
        )
