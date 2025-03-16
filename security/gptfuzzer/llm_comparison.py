import pandas as pd
from transformers import pipeline

# Function to test LLMs
def test_llms(models, prompts):
    results = []
    for model_name in models:
        print(f"Testing model: {model_name}")
        model = pipeline("text-generation", model=model_name)
        for prompt in prompts:
            response = model(prompt, max_length=50, truncation=True, pad_token_id=model.tokenizer.eos_token_id)[0]["generated_text"]
            results.append((model_name, prompt, response))
    return results

# Define models to test
# models = ["gpt2", "EleutherAI/gpt-j-6B", "mistralai/Mistral-7B"]
models = ["gpt2", "distilgpt2", "EleutherAI/gpt-neo-125M"]

# Load test prompts from a CSV file
df = pd.read_csv("test_prompts.csv")

# Run tests
test_results = test_llms(models, df["Mutated Prompt"])

# Save comparison results to a CSV file
df_results = pd.DataFrame(test_results, columns=["Model", "Prompt", "Response"])
df_results.to_csv("llm_comparison_results.csv", index=False)

print("Comparison complete. Results saved as llm_comparison_results.csv")



# (myenv) root@localhost:~/llm_tokenization# python llm_comparison_results.py
# 2025-03-12 17:48:05.576065: E external/local_xla/xla/stream_executor/cuda/cuda_fft.cc:477] Unable to register cuFFT factory: Attempting to register factory for plugin cuFFT when one has already been registered
# WARNING: All log messages before absl::InitializeLog() is called are written to STDERR
# E0000 00:00:1741801685.596387   40574 cuda_dnn.cc:8310] Unable to register cuDNN factory: Attempting to register factory for plugin cuDNN when one has already been registered
# E0000 00:00:1741801685.603513   40574 cuda_blas.cc:1418] Unable to register cuBLAS factory: Attempting to register factory for plugin cuBLAS when one has already been registered
# 2025-03-12 17:48:05.627574: I tensorflow/core/platform/cpu_feature_guard.cc:210] This TensorFlow binary is optimized to use available CPU instructions in performance-critical operations.
# To enable the following instructions: AVX2 FMA, in other operations, rebuild TensorFlow with the appropriate compiler flags.
# Testing model: gpt2
# Device set to use cpu
# Testing model: distilgpt2
# Device set to use cpu
# Testing model: EleutherAI/gpt-neo-125M
# Device set to use cpu
# Comparison complete. Results saved as llm_comparison_results.csv