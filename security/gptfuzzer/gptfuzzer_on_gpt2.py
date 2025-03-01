from transformers import pipeline
import pandas as pd

# Load dataset
df = pd.read_csv("fuzzing_prompts.csv")

# Load GPT-2 model
generator = pipeline("text-generation", model="gpt2")

# Run fuzz tests
results = []
for prompt in df["Mutated Prompt"]:
    output = generator(prompt, max_length=50, truncation=True, pad_token_id=generator.tokenizer.eos_token_id)
    results.append((prompt, output[0]["generated_text"]))

# Save results
df_results = pd.DataFrame(results, columns=["Prompt", "Response"])
df_results.to_csv("fuzzing_results.csv", index=False)

print("Testing complete. Results saved as fuzzing_results.csv")