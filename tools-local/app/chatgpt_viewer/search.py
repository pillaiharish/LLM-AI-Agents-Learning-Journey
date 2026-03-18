class ConversationSearch:
    @staticmethod
    def search(conversations: list, query: str) -> list:
        """Search across all conversations, return matching conversations with snippets."""
        if not query:
            return conversations

        query_lower = query.lower()
        results = []

        for conv in conversations:
            # Check title
            if query_lower in (conv.get("title", "") or "").lower():
                results.append(conv)
                continue

            # Check messages
            for msg in conv.get("messages", []):
                if query_lower in (msg.get("content", "") or "").lower():
                    results.append(conv)
                    break

        return results
