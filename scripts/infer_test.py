from transformers import AutoModelForCausalLM, LlamaTokenizer
import torch

MODEL_DIR = "../merged-models/combined-merged"

tokenizer = LlamaTokenizer.from_pretrained(MODEL_DIR, use_fast=False, local_files_only=True)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_DIR,
    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    device_map="auto",
    local_files_only=True
)

system_prompt = (
    "Du bist ein freundlicher Lernbegleiter für Kinder im Alter von 4–8 Jahren. "
    "Du erklärst Dinge kindgerecht, in einfacher Sprache, liebevoll und sicher."
)

def ask_model(user_prompt: str, max_new_tokens=128):
    full_prompt = f"<|system|>\n{system_prompt}\n<|user|>\n{user_prompt}\n<|assistant|>\n
