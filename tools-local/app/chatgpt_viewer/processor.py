import json
import os
from datetime import datetime


class ChatGPTProcessor:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.conversations_file = os.path.join(data_dir, "conversations.json")

    def process(self) -> list:
        """Parse conversations.json and return flattened conversation list."""
        if not os.path.exists(self.conversations_file):
            return []

        with open(self.conversations_file, "r", encoding="utf-8") as f:
            raw = json.load(f)

        conversations = []
        for conv in raw:
            try:
                processed = self._process_conversation(conv)
                if processed:
                    conversations.append(processed)
            except Exception:
                continue

        # Sort by create_time descending
        conversations.sort(key=lambda c: c.get("create_time_ts", 0), reverse=True)
        return conversations

    def _process_conversation(self, conv: dict) -> dict | None:
        conv_id = conv.get("id", conv.get("conversation_id", ""))
        title = conv.get("title", "Untitled")
        create_time = conv.get("create_time")
        mapping = conv.get("mapping", {})

        messages = self._flatten_messages(mapping)
        if not messages:
            return None

        create_str = ""
        create_ts = 0
        if create_time:
            try:
                create_ts = float(create_time)
                create_str = datetime.fromtimestamp(create_ts).strftime("%Y-%m-%d %H:%M")
            except (ValueError, TypeError, OSError):
                pass

        return {
            "id": conv_id,
            "title": title,
            "create_time": create_str,
            "create_time_ts": create_ts,
            "message_count": len(messages),
            "messages": messages,
        }

    def _flatten_messages(self, mapping: dict) -> list:
        """Flatten the message tree into ordered list."""
        messages = []
        visited = set()

        # Find root nodes (nodes with no parent or parent not in mapping)
        roots = []
        for node_id, node in mapping.items():
            parent = node.get("parent")
            if parent is None or parent not in mapping:
                roots.append(node_id)

        # DFS through the tree
        for root in roots:
            self._traverse(mapping, root, messages, visited)

        return messages

    def _traverse(self, mapping: dict, node_id: str, messages: list, visited: set):
        if node_id in visited:
            return
        visited.add(node_id)

        node = mapping.get(node_id, {})
        msg = node.get("message")

        if msg:
            role = msg.get("author", {}).get("role", "")
            content = msg.get("content", {})

            if role in ("user", "assistant") and content:
                parts = content.get("parts", [])
                text = ""
                for part in parts:
                    if isinstance(part, str):
                        text += part
                    elif isinstance(part, dict):
                        text += part.get("text", "")

                if text.strip():
                    messages.append({
                        "role": role,
                        "content": text,
                    })

        # Follow children
        children = node.get("children", [])
        for child_id in children:
            self._traverse(mapping, child_id, messages, visited)
