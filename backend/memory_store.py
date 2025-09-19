from collections import defaultdict


class ConversationMemory:
    def __init__(self):
        self.memory = defaultdict(list)

    def add_message(self, user_id: str, message: str, sender: str):
        self.memory[user_id].append({"sender": sender, "message": message})

    def get_context(self, user_id, limit=None):
        if limit:
            return self.memory[user_id][-limit:]
        return self.memory[user_id]

