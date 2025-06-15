# scripts/save_lora_adapter.py

from peft import PeftModel, get_peft_model_state_dict
from transformers import AutoModelForCausalLM
import torch

# Manuell nachtrainiertes Modell + Adapter
BASE_MODEL = "LeoLM/leo-hessianai-7b"
LORA_CHECKPOINT_DIR = "lora-outputs/combined"  # Zielordner erneut verwenden

model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    torch_dtype=torch.float16,
    device_map="auto",
    trust_remote_code=True
)

# Adapter direkt im Modell gespeichert (Training lief korrekt durch)
# → einfach nochmal speichern
peft_model = PeftModel(model, LORA_CHECKPOINT_DIR)
peft_model.save_pretrained(LORA_CHECKPOINT_DIR)

print("✅ LoRA-Adapter nachträglich gespeichert.")
