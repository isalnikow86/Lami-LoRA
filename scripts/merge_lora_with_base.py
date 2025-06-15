# scripts/merge_lora_with_base.py

from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Konfiguration
BASE_MODEL = "LeoLM/leo-hessianai-7b"
LORA_ADAPTER_PATH = "lora-outputs/combined"  # <-- passe hier an (z. B. "lora-outputs/klexikon")
MERGED_OUTPUT_PATH = "merged-models/combined-merged"

print("🔄 Lade Base-Model...")
base_model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    torch_dtype=torch.float16,
    device_map="auto",
    trust_remote_code=True
)

print("🔗 Lade LoRA-Adapter...")
merged_model = PeftModel.from_pretrained(base_model, LORA_ADAPTER_PATH)
merged_model = merged_model.merge_and_unload()  # wichtig!

print("💾 Speichere zusammengeführtes Modell...")
merged_model.save_pretrained(MERGED_OUTPUT_PATH)
AutoTokenizer.from_pretrained(BASE_MODEL).save_pretrained(MERGED_OUTPUT_PATH)

print(f"✅ Modell gespeichert unter: {MERGED_OUTPUT_PATH}")
