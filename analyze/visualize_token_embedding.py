import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
import matplotlib.pyplot as plt

# Load Universal Sentence Encoder
embed = hub.load("https://tfhub.dev/google/universal-sentence-encoder/4")

# Get embeddings
tokens = ["AI", "Artificial", "Intelligence", "Learning", "Deep"]
embeddings = embed(tokens)

# Plot embeddings
plt.scatter(embeddings[:, 0], embeddings[:, 1])
for i, token in enumerate(tokens):
    plt.annotate(token, (embeddings[i, 0], embeddings[i, 1]))
plt.show()
