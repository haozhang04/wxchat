from collections import deque

class ChatMemory:
    def __init__(self, max_len=20):
        self.history = deque(maxlen=max_len)

    def add_user_message(self, message):
        """Add a user message to the memory."""
        self.history.append({"role": "user", "content": message})

    def add_ai_message(self, message):
        """Add an AI message to the memory."""
        self.history.append({"role": "assistant", "content": message})

    def get_context(self):
        """Get the full conversation history as a list."""
        return list(self.history)

    def clear(self):
        """Clear the memory."""
        self.history.clear()
