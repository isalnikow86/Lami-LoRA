from peft import PeftModel
from transformers import AutoModelForCausalLM
import torch

# Base + bereits trainierter Adapter
BASE_MODEL = "LeoLM/leo-hessianai-7b"
LORA_CHECKPOINT_DIR = "lora-outputs/combined"

# Modell laden
model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    torch_dtype=torch.float16,
    device_map="auto",
    trust_remote_code=True
)

# LoRA-Adapterschichten laden aus bereits vorhandenem Verzeichnis
peft_model = PeftModel.from_pretrained(model, LORA_CHECKPOINT_DIR)

# Adapter erneut speichern, inkl. adapter_config.json
peft_model.save_pretrained(LORA_CHECKPOINT_DIR)

print("✅ LoRA-Adapter erfolgreich gespeichert.")
