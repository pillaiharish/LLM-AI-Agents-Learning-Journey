text = "Tokenization-free models are gaining popularity."
bytes_representation = [ord(c) for c in text]  # Convert characters to byte values
print("Byte-Level Representation:", bytes_representation)


# Output:
# (myenv) root@localhost:~/analyze# python byt5_process.py
# Byte-Level Representation: [84, 111, 107, 101, 110, 105, 122, 97, 116, 105, 111, 110, 45, 102, 114, 101, 101, 32, 109, 111, 100, 101, 108, 115, 32, 97, 114, 101, 32, 103, 97, 105, 110, 105, 110, 103, 32, 112, 111, 112, 117, 108, 97, 114, 105, 116, 121, 46]