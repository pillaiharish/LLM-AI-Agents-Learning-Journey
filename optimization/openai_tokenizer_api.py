import tiktoken

enc = tiktoken.get_encoding("cl100k_base")

text = "Understanding tokenization improves LLM efficiency."
tokens = enc.encode(text)

print("Tokenized Output:", tokens)
print("Decoded Tokens:", [enc.decode([t]) for t in tokens])

# (myenv) harish $ python openai_tokenizer_api.py 
# Tokenized Output: [71251, 4037, 2065, 36050, 445, 11237, 15374, 13]
# Decoded Tokens: ['Understanding', ' token', 'ization', ' improves', ' L', 'LM', ' efficiency', '.']