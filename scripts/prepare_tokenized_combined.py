# scripts/prepare_tokenized_combined.py

import json
from pathlib import Path
from datasets import Dataset
from transformers import AutoTokenizer

# === KONFIGURATION ===
DATA_FILES = [
    "data/kindersache_texts.jsonl",
    "data/oer_zum_texts.jsonl"
]
TOKENIZER_NAME = "LeoLM/leo-hessianai-7b"  # ✅ korrekt und öffentlich verfügbar
OUTPUT_PATH = "data/tokenized_combined"

def load_texts(files):
    all_texts = []
    for file in files:
        with open(file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    obj = json.loads(line)
                    # Nutze "text" oder "content" als Quelle
                    content = obj.get("text") or obj.get("content")
                    if content and len(content.strip()) > 20:
                        all_texts.append({"text": content.strip()})
                except json.JSONDecodeError:
                    continue
    return all_texts

def tokenize_dataset(texts, tokenizer_name):
    print(f"🔄 Lade Tokenizer: {tokenizer_name}")
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
    dataset = Dataset.from_list(texts)
    print(f"🔢 Tokenisiere {len(texts)} Texte...")
    tokenized = dataset.map(lambda x: tokenizer(x["text"], truncation=True, padding="max_length"), batched=True)
    return tokenized

if __name__ == "__main__":
    print("🚀 Starte Tokenizer-Vorbereitung...")
    texts = load_texts(DATA_FILES)
    print(f"✅ Geladene Texte: {len(texts)}")

    tokenized = tokenize_dataset(texts, TOKENIZER_NAME)

    Path(OUTPUT_PATH).mkdir(parents=True, exist_ok=True)
    tokenized.save_to_disk(OUTPUT_PATH)
    print(f"📦 Tokenisiertes Dataset gespeichert unter: {OUTPUT_PATH}")
