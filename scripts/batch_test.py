from transformers import LlamaTokenizer, LlamaForCausalLM
from pathlib import Path
import torch

MODEL_DIR = Path("/workspace/Lami-LoRA/merged-models/combined-merged")
PROMPT_FILE = Path("/workspace/Lami-LoRA/scripts/test_prompts.txt")

tokenizer = LlamaTokenizer.from_pretrained(MODEL_DIR, use_fast=False, local_files_only=True)
model = LlamaForCausalLM.from_pretrained(MODEL_DIR, torch_dtype=torch.float16, device_map="auto", local_files_only=True)

system_prompt = (
    "Du bist ein freundlicher Lernbegleiter für Kinder von 4–8 Jahren. "
    "Du erklärst Dinge in liebevoller, einfacher Sprache."
)

def ask(prompt):
    full_prompt = f"{system_prompt}\n\nFrage: {prompt}\nAntwort:"
    input_ids = tokenizer(full_prompt, return_tensors="pt").input_ids.to(model.device)
    with torch.no_grad():
        output = model.generate(input_ids, max_new_tokens=128)
    return tokenizer.decode(output[0], skip_special_tokens=True)

with open(PROMPT_FILE, "r") as f:
    prompts = [line.strip() for line in f if line.strip()]

for p in prompts:
    print(f"\n👦 Frage: {p}")
    print("🤖 Antwort:", ask(p))
