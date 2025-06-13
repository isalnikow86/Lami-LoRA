
import json
import os
from datasets import Dataset, DatasetDict
from transformers import AutoTokenizer

# Load tokenizer
base_model = "LeoLM/leo-hessianai-7b"
tokenizer = AutoTokenizer.from_pretrained(base_model)

# Load raw data
input_path = "data/oer_texts.jsonl"
with open(input_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

texts = [json.loads(line)["text"] for line in lines]

# Prepare HF Dataset
dataset = Dataset.from_dict({"text": texts})

# Tokenization function
def tokenize_function(examples):
    return tokenizer(
        examples["text"],
        padding="max_length",
        truncation=True,
        max_length=512,
    )

# Tokenize
tokenized_dataset = dataset.map(tokenize_function, batched=True, remove_columns=["text"])

# Save
output_path = "data/tokenized_oer_dataset"
tokenized_dataset.save_to_disk(output_path)

print(f"✅ Tokenized dataset saved to {output_path}")
