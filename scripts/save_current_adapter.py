import torch
from peft import get_peft_model, LoraConfig, TaskType
from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments
from datasets import load_from_disk

# Deine Trainingsparameter
base_model_id = "LeoLM/leo-hessianai-7b"
tokenized_path = "data/tokenized_combined"
output_path = "lora-outputs/combined"

# Modell laden
model = AutoModelForCausalLM.from_pretrained(
    base_model_id,
    device_map="auto",
    torch_dtype=torch.float16,
    trust_remote_code=True
)

# LoRA-Konfiguration wie beim Training
peft_config = LoraConfig(
    r=8,
    lora_alpha=16,
    lora_dropout=0.05,
    bias="none",
    task_type=TaskType.CAUSAL_LM
)

model = get_peft_model(model, peft_config)

# Dataset laden
dataset = load_from_disk(tokenized_path)

# Dummy TrainingArguments (Training wird nicht gestartet!)
training_args = TrainingArguments(
    output_dir=output_path,
    per_device_train_batch_size=1,
    num_train_epochs=1,
    save_steps=1,
    logging_steps=1,
    bf16=True,
    save_total_limit=1,
    save_strategy="no"  # wichtig!
)

# Nur LoRA-Modell speichern
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
    eval_dataset=None,
)

print("💾 Speichere LoRA-Adapter...")
model.save_pretrained(output_path)
print("✅ Adapter korrekt gespeichert in:", output_path)
