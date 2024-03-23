import json
import logging
from time import sleep
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


class SheetConsumer(WebsocketConsumer):
    def connect(self):
        self.sheet_name = self.scope["url_route"]["kwargs"]["sheet_name"]
        self.sheet_group_name = "sheet_%s" % self.sheet_name

        # Join sheet group
        async_to_sync(self.channel_layer.group_add)(
            self.sheet_group_name, self.channel_name
        )
        self.accept()

        for i in range(100):
            self.send(text_data=f"{i} ")
            sleep(0.1)
        self.disconnect()

    def disconnect(self, close_code):
        logging.debug("Websocket connection closed")
        async_to_sync(self.channel_layer.group_discard)(
            self.sheet_group_name, self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)

        # Send sheet_name to sheet group
        async_to_sync(self.channel_layer.group_send)(
            self.sheet_group_name,
            {
                "type": "refresh_sheet",
                "sheet_name": text_data_json["sheet_name"],
                "object_id": text_data_json["object_id"],
                "column_index": text_data_json["column_index"],
                "new_value": text_data_json["new_value"],
                "broadcaster_id": text_data_json["broadcaster_id"],
            },
        )

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
