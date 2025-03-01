import pandas as pd
from transformers import pipeline

# Load adversarial prompts
df = pd.read_csv("fuzzing_prompts.csv")

# Load GPT-2 model
generator = pipeline("text-generation", model="gpt2")

# Function to test the model
def test_model(prompts):
    results = []
    for prompt in prompts:
        output = generator(prompt, max_length=50, truncation=True, pad_token_id=generator.tokenizer.eos_token_id)
        response = output[0]["generated_text"]
        results.append((prompt, response))
    return results

# Run the test
test_results = test_model(df["Mutated Prompt"])

# Save results
df_results = pd.DataFrame(test_results, columns=["Prompt", "Response"])
df_results.to_csv("llm_fuzzing_results.csv", index=False)

print("Testing complete. Results saved as llm_fuzzing_results.csv")