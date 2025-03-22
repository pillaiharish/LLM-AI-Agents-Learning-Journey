from transformers import BertForMaskedLM, BertTokenizer, pipeline

# Load the trained model and tokenizer
model = BertForMaskedLM.from_pretrained("./bert_pretraining/checkpoint-125")
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")

# Create a fill-mask pipeline
fill_mask = pipeline("fill-mask", model=model, tokenizer=tokenizer)

print(fill_mask("The capital of France is [MASK]."),"\n")
print(fill_mask("Artificial intelligence is changing the [MASK]."),"\n")
print(fill_mask("The Eiffel Tower is located in [MASK]."),"\n")


# Output:
# Device set to use cpu

# [{'score': 0.5166928768157959, 'token': 3000, 'token_str': 'paris', 'sequence': 'the capital of france is paris.'}, {'score': 0.07590827345848083, 'token': 10241, 'token_str': 'lyon', 'sequence': 'the capital of france is lyon.'}, {'score': 0.05815894529223442, 'token': 22479, 'token_str': 'lille', 'sequence': 'the capital of france is lille.'}, {'score': 0.03797366842627525, 'token': 16766, 'token_str': 'marseille', 'sequence': 'the capital of france is marseille.'}, {'score': 0.037093620747327805, 'token': 7562, 'token_str': 'tours', 'sequence': 'the capital of france is tours.'}]

# [{'score': 0.9266387820243835, 'token': 2088, 'token_str': 'world', 'sequence': 'artificial intelligence is changing the world.'}, {'score': 0.027996480464935303, 'token': 5304, 'token_str': 'universe', 'sequence': 'artificial intelligence is changing the universe.'}, {'score': 0.0045710233971476555, 'token': 2208, 'token_str': 'game', 'sequence': 'artificial intelligence is changing the game.'}, {'score': 0.004185487981885672, 'token': 4044, 'token_str': 'environment', 'sequence': 'artificial intelligence is changing the environment.'}, {'score': 0.0030182439368218184, 'token': 2925, 'token_str': 'future', 'sequence': 'artificial intelligence is changing the future.'}]

# [{'score': 0.5650281310081482, 'token': 3000, 'token_str': 'paris', 'sequence': 'the eiffel tower is located in paris.'}, {'score': 0.06534846127033234, 'token': 2605, 'token_str': 'france', 'sequence': 'the eiffel tower is located in france.'}, {'score': 0.06281246244907379, 'token': 10765, 'token_str': 'luxembourg', 'sequence': 'the eiffel tower is located in luxembourg.'}, {'score': 0.03313761577010155, 'token': 9371, 'token_str': 'brussels', 'sequence': 'the eiffel tower is located in brussels.'}, {'score': 0.0145595483481884, 'token': 14497, 'token_str': 'monaco', 'sequence': 'the eiffel tower is located in monaco.'}]
