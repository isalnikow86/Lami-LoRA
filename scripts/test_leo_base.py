from transformers import LlamaTokenizer, LlamaForCausalLM
import torch

MODEL_DIR = "/workspace/Lami-LoRA/leo-hessianai-7b"  # ← Dein lokaler Pfad

tokenizer = LlamaTokenizer.from_pretrained(
    MODEL_DIR, use_fast=False, local_files_only=True
)
model = LlamaForCausalLM.from_pretrained(
    MODEL_DIR,
    torch_dtype=torch.float16,
    device_map="auto",
    local_files_only=True,
    trust_remote_code=True  # ← Wichtig für modeling_flash_llama.py
)

def ask(question: str):
    prompt = (
        "Du bist ein liebevoller Lernbegleiter für Kinder von 4–8 Jahren. "
        "Erkläre Dinge in einfacher Sprache.\n\n"
        f"Frage: {question}\nAntwort:"
    )

    input_ids = tokenizer(prompt, return_tensors="pt").input_ids.to(model.device)

    with torch.no_grad():
        output_ids = model.generate(
            input_ids,
            max_new_tokens=100,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=tokenizer.eos_token_id
        )

    new_tokens = output_ids[0][input_ids.shape[1]:]
    output_text = tokenizer.decode(new_tokens, skip_special_tokens=True)
    return output_text.strip()

frage = "Was ist ein Stern?"
print("👦 Frage:", frage)
print("🤖 Antwort:", ask(frage))
