from transformers import AutoTokenizer

# Load BERT tokenizer
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

# Tokenize a sample text
sample_text = "Albert Einstein was a [MASK] physicist."
tokens = tokenizer(sample_text, return_tensors="pt")

print(tokens)


# Output:
# $ python tokenize_for_model.py 
# {'input_ids': tensor([[  101,  4789, 15313,  2001,  1037,   103, 13702,  1012,   102]]), 'token_type_ids': tensor([[0, 0, 0, 0, 0, 0, 0, 0, 0]]), 'attention_mask': tensor([[1, 1, 1, 1, 1, 1, 1, 1, 1]])}