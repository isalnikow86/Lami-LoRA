import argparse
import yaml
from datasets import load_from_disk
from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments
from peft import get_peft_model, LoraConfig, TaskType
import torch

# Parse args
parser = argparse.ArgumentParser()
parser.add_argument("--config", type=str, required=True)
args = parser.parse_args()

# Load config
with open(args.config, "r") as f:
    config = yaml.safe_load(f)

# Load base model + tokenizer
model = AutoModelForCausalLM.from_pretrained(config["base_model"])
tokenizer = AutoTokenizer.from_pretrained(config["base_model"])

# Prepare LoRA
peft_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type=TaskType.CAUSAL_LM,
)

model = get_peft_model(model, peft_config)

# Load dataset
dataset = load_from_disk("data/tokenized_klexikon_dataset")

# Training args
training_args = TrainingArguments(
    output_dir=config["output_dir"],
    per_device_train_batch_size=config["batch_size"],
    learning_rate = float(config["learning_rate"]),
    num_train_epochs=config["num_train_epochs"],
    logging_dir="./logs",
    logging_steps=config["logging_steps"],
    save_steps=config["save_steps"],
    save_total_limit=2,
    evaluation_strategy="no",
    fp16=True,
    report_to="none",
)

# Data collator
def data_collator(features):
    batch = {}
    batch["input_ids"] = [f["input_ids"] for f in features]
    batch["attention_mask"] = [f["attention_mask"] for f in features]
    batch["labels"] = batch["input_ids"].copy()
    return {k: torch.tensor(v) for k, v in batch.items()}

# Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset = dataset.with_format("torch"),
    eval_dataset=dataset["validation"],
    tokenizer=tokenizer,
    gradient_checkpointing=True,  # <== HIER ergänzen!
)


# Train
trainer.train()
trainer.save_model(config["output_dir"])
tokenizer.save_pretrained(config["output_dir"])

print("LoRA training completed and model saved.")
