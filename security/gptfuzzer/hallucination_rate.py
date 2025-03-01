import pandas as pd

# Load the dataset
df = pd.read_csv("llm_hallucination_fuzz.csv")

# Define hallucination keywords
hallucination_keywords = [
    "NASA found alien life", "Apple acquired Microsoft", "India colonized Britain",
    "the moon is made of cheese", "Einstein invented the internet"
]

# Function to check hallucinations
def check_hallucination(response):
    return any(keyword in response for keyword in hallucination_keywords)

# Apply the function to the Response column
df["Hallucination"] = df["Response"].apply(check_hallucination)

# Calculate hallucination rate
hallucination_rate = df["Hallucination"].mean() * 100
print(f"Hallucination Rate: {hallucination_rate:.2f}%")

# Optional: Print rows with hallucinations
print("\nResponses with Hallucinations:")
print(df[df["Hallucination"] == True])