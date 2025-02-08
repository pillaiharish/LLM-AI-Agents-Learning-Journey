import tiktoken

enc = tiktoken.get_encoding("cl100k_base")

print(enc.encode("Hello, world!"))  



# Output: 
# $ python3 tiktoken_encodeing.py 
# [9906, 11, 1917, 0]