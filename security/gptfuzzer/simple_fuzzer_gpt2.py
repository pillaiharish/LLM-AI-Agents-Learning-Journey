from transformers import pipeline

# Load the GPT-2 model
generator = pipeline("text-generation", model="gpt2")

# Define a simple test prompt
prompt = "Explain the importance of cybersecurity."

# Generate a response with explicit truncation and padding settings
output = generator(prompt, max_length=300, truncation=True, pad_token_id=generator.tokenizer.eos_token_id)

# Print the generated text
print(output[0]['generated_text'])