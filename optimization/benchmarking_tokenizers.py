import time
from transformers import AutoTokenizer

text = "Machine learning models depend on efficient tokenization."

# Load different tokenizers
tokenizers = {
    "GPT-4": AutoTokenizer.from_pretrained("gpt2"),
    "Mistral": AutoTokenizer.from_pretrained("mistralai/Mistral-7B-v0.1"),
}

for name, tokenizer in tokenizers.items():
    start_time = time.time()
    tokens = tokenizer.tokenize(text)
    elapsed_time = time.time() - start_time
    compression_ratio = len(text) / len(tokens)

    print(f"{name} - Tokens: {len(tokens)}, Time: {elapsed_time:.6f} sec, Compression Ratio: {compression_ratio:.2f}")


# Output:
# GPT-4 - Tokens: 9, Time: 0.001713 sec, Compression Ratio: 6.33
# Mistral - Tokens: 9, Time: 0.000069 sec, Compression Ratio: 6.33