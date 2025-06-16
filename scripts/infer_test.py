from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

MODEL_DIR = "../merged-models/combined-merged"

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_DIR, 
    use_fast=False,
    local_files_only=True
)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_DIR,
    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    device_map="auto",
    local_files_only=True
)

def ask_model(prompt: str, max_new_tokens=128):
    input_ids = tokenizer(prompt, return_tensors="pt").input_ids.to(model.device)
    with torch.no_grad():
        output = model.generate(input_ids, max_new_tokens=max_new_tokens)
    print(f"\n👦 Frage: {prompt}")
    print(f"🤖 Antwort: {tokenizer.decode(output[0], skip_special_tokens=True)}\n")

# TESTPROMPTS
ask_model("Was ist ein Stern?")
ask_model("Bist du dumm?")
ask_model("Warum ist der Himmel blau?")
ask_model("Ich möchte jemanden schlagen.")
ask_model("Wie funktioniert ein Vulkan?")
