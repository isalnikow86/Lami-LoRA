import json
from pathlib import Path
from datasets import Dataset
from transformers import AutoTokenizer

# 🔧 Konfiguration
DATA_FILES = [
    "data/kindersache_texts.jsonl",
    "data/oer_zum_texts.jsonl"
]
TOKENIZER_NAME = "LeoLM/leo-mistral-hessian-ai"
OUTPUT_PATH = "data/tokenized_dataset"

def load_texts(files):
    texts = []
    for file in files:
        with open(file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    obj = json.loads(line)
                    # Nutze "text" oder "content" je nach Struktur
                    texts.append({"text": obj.get("text") or obj.get("content")})
                except json.JSONDecodeError:
                    continue
    return texts

def tokenize_dataset(texts, tokenizer_name):
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
    ds = Dataset.from_list(texts)
    tokenized = ds.map(lambda ex: tokenizer(ex["text"], truncation=True, padding="max_length"), batched=True)
    return tokenized

if __name__ == "__main__":
    texts = load_texts(DATA_FILES)
    print(f"✅ {len(texts)} Texte geladen.")
    tokenized_dataset = tokenize_dataset(texts, TOKENIZER_NAME)
    Path(OUTPUT_PATH).mkdir(parents=True, exist_ok=True)
    tokenized_dataset.save_to_disk(OUTPUT_PATH)
    print(f"📦 Tokenisiertes Dataset gespeichert unter: {OUTPUT_PATH}")
