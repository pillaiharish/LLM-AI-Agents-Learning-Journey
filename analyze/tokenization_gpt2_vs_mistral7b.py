from transformers import AutoTokenizer

# Load different tokenizers
gpt2_tokenizer = AutoTokenizer.from_pretrained("gpt2")
mistral_tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-v0.1")

text = "Understanding LLMs requires deep learning."

gpt2_tokens = gpt2_tokenizer.tokenize(text)
mistral_tokens = mistral_tokenizer.tokenize(text)

print("GPT-2 Tokenization:", gpt2_tokens)
print("Mistral-7B Tokenization:", mistral_tokens)


# Output 1:
# (myenv) harish:analyze $ python tokenization_gpt2_vs_llama.py 
# None of PyTorch, TensorFlow >= 2.0, or Flax have been found. Models won't be available and only tokenizers, configuration and file/data utilities can be used.
# tokenizer_config.json: 100%|████████████████████████████████████████████████████████████████████████████████| 996/996 [00:00<00:00, 2.84MB/s]
# tokenizer.model: 100%|████████████████████████████████████████████████████████████████████████████████████| 493k/493k [00:00<00:00, 3.34MB/s]
# tokenizer.json: 100%|███████████████████████████████████████████████████████████████████████████████████| 1.80M/1.80M [00:00<00:00, 2.38MB/s]
# special_tokens_map.json: 100%|██████████████████████████████████████████████████████████████████████████████| 414/414 [00:00<00:00, 1.24MB/s]
# GPT-2 Tokenization: ['Understanding', 'ĠLL', 'Ms', 'Ġrequires', 'Ġdeep', 'Ġlearning', '.']
# Mistral-7B Tokenization: ['▁Under', 'standing', '▁LL', 'Ms', '▁requires', '▁deep', '▁learning', '.']



text = "AI-powered models improve performance in NLPTasks."

# Debug tokenization for different models
print("GPT-2 Tokens:", gpt2_tokenizer.tokenize(text))
print("Mistral-7B Tokens:", mistral_tokenizer.tokenize(text))


# Output 2:
# GPT-2 Tokens: ['AI', '-', 'powered', 'Ġmodels', 'Ġimprove', 'Ġperformance', 'Ġin', 'ĠNL', 'PT', 'asks', '.']
# Mistral-7B Tokens: ['▁AI', '-', 'powered', '▁models', '▁improve', '▁performance', '▁in', '▁N', 'LP', 'Tasks', '.']