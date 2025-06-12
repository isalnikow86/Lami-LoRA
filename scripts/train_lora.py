import os
import yaml
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments
from datasets import load_from_disk

# Load config
with open("configs/lora_config.yaml") as f:
    config = yaml.safe_load(f)

# Load model + tokenizer
model = AutoModelForCausalLM.from_pretrained(config["base_model"])
tokenizer = AutoTokenizer.from_pretrained(config["base_model"])

# Load dataset
dataset = load_from_disk("data/tokenized_klexikon_dataset")

# Define TrainingArguments
training_args = TrainingArguments(
    output_dir=config["output_dir"],
    learning_rate = float(config["learning_rate"]),
    per_device_train_batch_size=config["batch_size"],
    num_train_epochs=config["num_train_epochs"],
    logging_steps=config["logging_steps"],
    save_steps=config["save_steps"],
    gradient_checkpointing=True,   # richtig hier
)

# Define Data Collator
def data_collator(features):
    batch = {}
    batch["input_ids"] = torch.tensor([f["input_ids"] for f in features], dtype=torch.long)
    batch["attention_mask"] = torch.tensor([f["attention_mask"] for f in features], dtype=torch.long)
    batch["labels"] = batch["input_ids"].clone()
    return batch


# Define Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset.with_format("torch"),
    eval_dataset=None,  # Keine Validation
    tokenizer=tokenizer,
    data_collator=data_collator,  # wichtig!
)

# Run training
trainer.train()

# Save model + tokenizer
trainer.save_model(config["output_dir"])
tokenizer.save_pretrained(config["output_dir"])

print("LoRA training completed and model saved.")
