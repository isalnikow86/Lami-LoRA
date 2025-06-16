from transformers import LlamaTokenizer, LlamaForCausalLM
from pathlib import Path
import torch

MODEL_DIR = Path("/workspace/Lami-LoRA/merged-models/combined-merged")
PROMPT_FILE = Path("/workspace/Lami-LoRA/scripts/test_prompts.txt")

tokenizer = LlamaTokenizer.from_pretrained(
    MODEL_DIR, use_fast=False, local_files_only=True
)
model = LlamaForCausalLM.from_pretrained(
    MODEL_DIR,
    torch_dtype=torch.float16,
    device_map="auto",
    local_files_only=True
)

# ✅ EINMAL definiert
system_prompt = (
    "Du bist ein liebevoller Lernbegleiter für Kinder im Alter von 4–8 Jahren. "
    "Antworte ruhig, freundlich und einfach."
)

def ask(user_prompt: str, max_new_tokens=100):
    full_prompt = f"{system_prompt}\n\nFrage: {user_prompt}\nAntwort:"
    input_ids = tokenizer(full_prompt, return_tensors="pt").input_ids.to(model.device)

    with torch.no_grad():
        output_ids = model.generate(
            input_ids,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=tokenizer.eos_token_id
        )

    # Nur neue Tokens extrahieren
    new_tokens = output_ids[0][input_ids.shape[1]:]
    output_text = tokenizer.decode(new_tokens, skip_special_tokens=True)
    return output_text.strip()

# 📥 Promptliste laden
with open(PROMPT_FILE, "r") as f:
    prompts = [line.strip() for line in f if line.strip()]

# 🔁 Testausgabe
for p in prompts:
    print(f"\n👦 Frage: {p}")
    print("🤖 Antwort:", ask(p))
