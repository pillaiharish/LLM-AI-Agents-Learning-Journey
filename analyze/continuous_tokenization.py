import queue

def stream_tokenization(text_stream):
    token_queue = queue.Queue()
    for word in text_stream.split():
        token_queue.put(word)
        print("Tokenized:", token_queue.get())

text_input = "Streaming tokenization is useful for live applications."
stream_tokenization(text_input)


# Output:
# (myenv) root@localhost:~/analyze# python continuous_tokenization.py
# Tokenized: Streaming
# Tokenized: tokenization
# Tokenized: is
# Tokenized: useful
# Tokenized: for
# Tokenized: live
# Tokenized: applications.