from typing import Dict, List


class ConversationMemory:

    def __init__(self, max_length: int = 20):
        self.max_length = max_length
        self.messages: List[Dict[str, str]] = []

    def add_user_message(self, content: str) -> None:
        self.messages.append({"role": "user", "content": content})
        self._trim()

    def add_assistant_message(self, content: str) -> None:
        self.messages.append({"role": "assistant", "content": content})
        self._trim()

    def get_messages(self) -> List[Dict[str, str]]:
        return list(self.messages)

    def get_history_text(self) -> str:
        return "\n".join(
            f"{message['role'].capitalize()}: {message['content']}"
            for message in self.messages
        )

    def clear(self) -> None:
        self.messages.clear()

    def _trim(self) -> None:
        if len(self.messages) > self.max_length:
            self.messages = self.messages[-self.max_length:]
