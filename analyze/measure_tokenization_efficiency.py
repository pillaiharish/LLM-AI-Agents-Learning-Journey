import time
from transformers import AutoTokenizer

text = "Tokenization strategies impact model efficiency."

# Load different tokenizers
tokenizers = {
    "GPT-4 (BPE)": AutoTokenizer.from_pretrained("gpt2"),
    "Falcon (BPE)": AutoTokenizer.from_pretrained("tiiuae/falcon-7b"),
    "OpenLLaMA (SentencePiece)": AutoTokenizer.from_pretrained("openlm-research/open_llama_7b"),
}

for name, tokenizer in tokenizers.items():
    start_time = time.time()
    tokens = tokenizer.tokenize(text)
    elapsed_time = time.time() - start_time
    print(f"{name} - Tokens: {len(tokens)}, Time: {elapsed_time:.6f} sec")


# Output:
# (myenv) root@localhost:~/analyze# python measure_tokenization_efficiency.py
# You are using the default legacy behaviour of the <class 'transformers.models.llama.tokenization_llama.LlamaTokenizer'>. This is expected, and simply means that the `legacy` (previous) behavior will be used so nothing changes for you. If you want to use the new behaviour, set `legacy=False`. This should only be set if you understand what it means, and thoroughly read the reason why this was added as explained in https://github.com/huggingface/transformers/pull/24565 - if you loaded a llama tokenizer from a GGUF file you can ignore this message
# You are using the default legacy behaviour of the <class 'transformers.models.llama.tokenization_llama_fast.LlamaTokenizerFast'>. This is expected, and simply means that the `legacy` (previous) behavior will be used so nothing changes for you. If you want to use the new behaviour, set `legacy=False`. This should only be set if you understand what it means, and thoroughly read the reason why this was added as explained in https://github.com/huggingface/transformers/pull/24565 - if you loaded a llama tokenizer from a GGUF file you can ignore this message.
# GPT-4 (BPE) - Tokens: 7, Time: 0.001095 sec
# Falcon (BPE) - Tokens: 7, Time: 0.000205 sec
# OpenLLaMA (SentencePiece) - Tokens: 8, Time: 0.000165 sec