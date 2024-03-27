import json
import logging
from typing import Any, Dict
from langchain.memory.summary_buffer import ConversationSummaryBufferMemory
from langchain_community.chat_message_histories.in_memory import ChatMessageHistory
from langchain.schema import messages_from_dict, messages_to_dict

from companion.db.utils import UserId, redis


class RedisConversationSummaryBufferMemory(ConversationSummaryBufferMemory):
    user_id: UserId

    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        """Save context from this conversation to buffer."""
        super().save_context(inputs, outputs)

    def get_memory_key(self) -> str:
        return f"companion:memory:{self.user_id}:activity"

    def persist(self):
        if not isinstance(self.chat_memory, ChatMessageHistory):
            raise NotImplementedError(
                "Only in memory ChatMessageHistory is supported for database storage"
            )
        redis().set(self.get_memory_key(), json.dumps(messages_to_dict(self.chat_memory.messages)))

    def fetch_from_db(self):
        serialized_messages = redis().get(self.get_memory_key())
        if not serialized_messages:
            return
        messages = messages_from_dict(json.loads(serialized_messages))
        self.chat_memory = ChatMessageHistory(messages=messages)
        n_messages = len(self.chat_memory.messages)
        if n_messages > 0:
            logging.info(f"User {self.user_id} fetched {n_messages} messages from DB")
