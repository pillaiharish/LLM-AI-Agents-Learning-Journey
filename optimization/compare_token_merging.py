from transformers import AutoTokenizer, AutoModelForMaskedLM
from transformers import BertTokenizer, BertModel
text = "Artificial Intelligence transforms industries."

# Load different tokenization models
bpe_tokenizer = AutoTokenizer.from_pretrained("gpt2")
unigram_tokenizer = BertModel.from_pretrained("bert-base-uncased") #AutoModelForMaskedLM.from_pretrained("google/bert-base-uncased", token)

print("BPE Tokenization:", bpe_tokenizer.tokenize(text))
print("Unigram Tokenization:", unigram_tokenizer.tokenize(text))

# BPE Tokenization: ['Art', 'ificial', 'ĠIntelligence', 'Ġtransforms', 'Ġindustries', '.']
# Unigram Tokenization: ['artificial', 'intelligence', 'transforms', 'industries', '.']