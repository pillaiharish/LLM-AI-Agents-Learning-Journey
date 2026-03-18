import tiktoken


class TokenCounter:
    _encodings: dict = {}

    @classmethod
    def _get_encoding(cls, encoding_name: str):
        if encoding_name not in cls._encodings:
            cls._encodings[encoding_name] = tiktoken.get_encoding(encoding_name)
        return cls._encodings[encoding_name]

    @staticmethod
    def count_tiktoken(text: str, encoding_name: str) -> int:
        enc = TokenCounter._get_encoding(encoding_name)
        return len(enc.encode(text))

    @staticmethod
    def count_heuristic(text: str) -> int:
        words = len(text.split())
        return max(1, int(words * 1.3))

    @staticmethod
    def count_for_model(text: str, model_config: dict) -> dict:
        encoding = model_config.get("tokenizer_encoding")
        heuristic = TokenCounter.count_heuristic(text)

        if encoding:
            try:
                exact = TokenCounter.count_tiktoken(text, encoding)
                return {
                    "token_count": exact,
                    "method": "tiktoken",
                    "heuristic_count": heuristic,
                }
            except Exception:
                pass

        return {
            "token_count": heuristic,
            "method": "heuristic (~1.3 tokens/word)",
            "heuristic_count": heuristic,
        }
