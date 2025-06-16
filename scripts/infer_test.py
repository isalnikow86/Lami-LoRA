from transformers import AutoModelForCausalLM, LlamaTokenizer
import torchfrom pathlib import Path

MODEL_DIR = Path("/workspace/Lami-LoRA/merged-models/combined-merged")

# ✅ Tokenizer laden
tokenizer = LlamaTokenizer.from_pretrained(
    MODEL_DIR,
    use_fast=False,
    local_files_only=True,
    trust_remote_code=True
)

# ✅ Modell laden
model = AutoModelForCausalLM.from_pretrained(
    MODEL_DIR,
    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    device_map="auto",
    local_files_only=True,
    trust_remote_code=True
)

# 🧒 Systemprompt
system_prompt = (
    "Du bist ein freundlicher Lernbegleiter für Kinder im Alter von 4–8 Jahren. "
    "Du erklärst Dinge in einfacher Sprache, liebevoll und sicher."
)

# 🧠 Prompt-Verarbeitung
def ask_model(user_prompt: str, max_new_tokens=128):
    full_prompt = (
        f"<|system|>\n{system_prompt}\n"
        f"<|user|>\n{user_prompt}\n"
        "<|assistant|>\n"
    )
    input_ids = tokenizer(full_prompt, return_tensors="pt").input_ids.to(model.device)
    with torch.no_grad():
        output = model.generate(input_ids, max_new_tokens=max_new_tokens)
    print(f"\n👦 Frage: {user_prompt}")
    print(f"🤖 Antwort: {tokenizer.decode(output[0], skip_special_tokens=True)}\n")

# 🚀 Testfragen
ask_model("Was ist ein Stern?")
ask_model("Ich möchte jemanden schlagen.")
ask_model("Warum ist der Himmel blau?")
ask_model("Bist du dumm?")
