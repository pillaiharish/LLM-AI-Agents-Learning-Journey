from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("gpt2")

print(tokenizer.tokenize("Hello, world!"))  

# Output: [
# (myenv) harish:analyze $ python tokenize_hugging_face.py 
# None of PyTorch, TensorFlow >= 2.0, or Flax have been found. Models won't be available and only tokenizers, configuration and file/data utilities can be used.
# tokenizer_config.json: 100%|██████████████████████████████████████████████████████████████████████████████| 26.0/26.0 [00:00<00:00, 82.5kB/s]
# config.json: 100%|██████████████████████████████████████████████████████████████████████████████████████████| 665/665 [00:00<00:00, 3.93MB/s]
# vocab.json: 100%|███████████████████████████████████████████████████████████████████████████████████████| 1.04M/1.04M [00:00<00:00, 1.38MB/s]
# merges.txt: 100%|██████████████████████████████████████████████████████████████████████████████████████████| 456k/456k [00:00<00:00, 939kB/s]
# tokenizer.json: 100%|███████████████████████████████████████████████████████████████████████████████████| 1.36M/1.36M [00:00<00:00, 3.02MB/s]
# ['Hello', ',', 'Ġworld', '!']