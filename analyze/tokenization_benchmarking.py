import time
from transformers import AutoTokenizer

text = "Efficient tokenization can improve LLM inference speed significantly."

tokenizers = {
    "GPT2": AutoTokenizer.from_pretrained("gpt2"),
    "XLM-R": AutoTokenizer.from_pretrained("xlm-roberta-base")
}

for name, tokenizer in tokenizers.items():
    start = time.time()
    tokens = tokenizer.tokenize(text)
    end = time.time()
    print(f"{name} took {(end - start)*1000:.2f} ms and produced {len(tokens)} tokens")


# Output:
# (myenv) root@localhost:~/analyze# python tokenization_benchmarking.py
# GPT2 took 1.03 ms and produced 12 tokens
# XLM-R took 0.38 ms and produced 15 tokens