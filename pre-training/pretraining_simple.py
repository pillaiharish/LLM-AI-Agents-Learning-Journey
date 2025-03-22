from datasets import load_dataset
from transformers import BertForMaskedLM, Trainer, TrainingArguments, BertTokenizer, DataCollatorForLanguageModeling

# Step 1: Load a small subset of the dataset
dataset = load_dataset("wikipedia", "20220301.simple", split="train[:1000]")  # Load only 1000 examples

# Step 2: Load the pre-trained BERT model and tokenizer
model = BertForMaskedLM.from_pretrained("bert-base-uncased")
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")

# Step 3: Tokenize the dataset
def tokenize_function(examples):
    return tokenizer(examples["text"], padding="max_length", truncation=True, max_length=128)  # Reduce max_length

tokenized_dataset = dataset.map(tokenize_function, batched=True, remove_columns=["text"])

# Step 4: Prepare the data collator for MLM
data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=True,  # Enable masked language modeling
    mlm_probability=0.15  # Mask 15% of tokens
)

# Step 5: Define training arguments
training_args = TrainingArguments(
    output_dir="./bert_pretraining",
    per_device_train_batch_size=8,  # Adjust based on your hardware
    logging_dir="./logs",
    num_train_epochs=1,
    save_steps=10_000,
    save_total_limit=2,
)

# Step 6: Create Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
    data_collator=data_collator,  # Use the data collator for MLM
)

# Step 7: Start training
trainer.train(resume_from_checkpoint=True)

# Output:
# Map: 100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████| 1000/1000 [00:18<00:00, 52.71 examples/s]
# {'train_runtime': 825.5566, 'train_samples_per_second': 1.211, 'train_steps_per_second': 0.151, 'train_loss': 1.7452313232421874, 'epoch': 1.0}
# 100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 125/125 [13:45<00:00,  6.60s/it]
