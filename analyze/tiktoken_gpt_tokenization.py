import tiktoken

# Load OpenAI's tokenizer (GPT-4)
enc = tiktoken.get_encoding("cl100k_base")

text = "Tokenization is important in NLP models."
tokens = enc.encode(text)

print("Tokenized Output:", tokens)
print("Decoded Tokens:", [enc.decode([t]) for t in tokens])

# Output: 
# $ python tiktoken_gpt_tokenization.py 
# Tokenized Output: [3404, 2065, 374, 3062, 304, 452, 12852, 4211, 13]
# Decoded Tokens: ['Token', 'ization', ' is', ' important', ' in', ' N', 'LP', ' models', '.']