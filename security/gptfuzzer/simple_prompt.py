import random

def mutate_prompt(prompt):
    mutations = [
        lambda x: x.replace("a", "@"),  # Character substitution
        lambda x: x.replace("e", "3"),  # Leetspeak
        lambda x: x + " 🤖🚀",  # Append special characters
        lambda x: x.upper(),  # Convert to uppercase
        lambda x: x[::-1]  # Reverse the string
    ]
    return random.choice(mutations)(prompt)

# Define a test prompt
original_prompt = "Explain cybersecurity risks."
mutated_prompt = mutate_prompt(original_prompt)

print(f"Original: {original_prompt}")
print(f"Mutated: {mutated_prompt}")