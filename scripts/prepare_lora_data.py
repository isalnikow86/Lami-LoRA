import json
from datasets import Dataset
from transformers import AutoTokenizer

MODEL_NAME = "LeoLM/leo-hessianai-7b"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

# Load Klexikon data
with open("data/klexikon_texts.jsonl", "r", encoding="utf-8") as f:
    lines = [json.loads(line) for line in f]

texts = [line["text"] for line in lines]

# Create Huggingface Dataset
dataset = Dataset.from_dict({"text": texts})

# Tokenize
def tokenize(batch):
    return tokenizer(batch["text"], truncation=True, padding="max_length", max_length=512)

tokenized_dataset = dataset.map(tokenize, batched=True, remove_columns=["text"])
tokenized_dataset.save_to_disk("data/tokenized_klexikon_dataset")
print("Tokenized dataset saved.")
