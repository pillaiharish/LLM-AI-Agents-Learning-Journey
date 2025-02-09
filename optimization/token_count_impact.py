from transformers import AutoTokenizer

text = "Artificial Intelligence is transforming the world."

# Using GPT-4 Tokenizer
gpt4_tokenizer = AutoTokenizer.from_pretrained("gpt2")
gpt4_tokens = gpt4_tokenizer.tokenize(text)

# Using a Custom Tokenizer with a Larger Vocabulary
custom_tokenizer = AutoTokenizer.from_pretrained("bigscience/bloom")
custom_tokens = custom_tokenizer.tokenize(text)

print("GPT-4 Token Count:", len(gpt4_tokens))
print("Custom Tokenizer Token Count:", len(custom_tokens))


# Output:
# (myenv) harish:optimization $ python token_count_impact.py 
# GPT-4 Token Count: 8
# Custom Tokenizer Token Count: 8