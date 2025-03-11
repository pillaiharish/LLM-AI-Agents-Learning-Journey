from transformers import AutoTokenizer

text = "मैंने Artificial Intelligence का उपयोग किया।"

tokenizer = AutoTokenizer.from_pretrained("ai4bharat/indic-bert")
print("Multilingual Tokenization:", tokenizer.tokenize(text))


# (myenv) harish $ python code_switched_text_handle.py 
# Multilingual Tokenization: ['▁मन', '▁artificial', '▁intelligence', '▁क', '▁उप', 'य', 'ग', '▁क', 'य', '।']