import os
import yaml
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments
from datasets import load_from_disk

# Load config
with open("configs/lora_config.yaml") as f:
    config = yaml.safe_load(f)

# Load model + tokenizer
model = AutoModelForCausalLM.from_pretrained(
    config["base_model"],
    device_map="auto",
    trust_remote_code=True,
    torch_dtype=torch.float16  # wichtig für H100 stabil
)
tokenizer = AutoTokenizer.from_pretrained(config["base_model"])

# Load dataset
dataset = load_from_disk("data/tokenized_klexikon_dataset")

# Define TrainingArguments
training_args = TrainingArguments(
    output_dir=config["output_dir"],
    learning_rate=float(config["learning_rate"]),
    per_device_train_batch_size=config["batch_size"],
    num_train_epochs=config["num_train_epochs"],
    logging_steps=config["logging_steps"],
    save_steps=config["save_steps"],
    gradient_checkpointing=False,  # für Stabilität, FP16 + H100 + bnb safe
    bf16=True,  # H100 unterstützt BF16 → effizient
    fp16=False,  # wenn bf16 geht → kein fp16 zusätzlich
    optim="adamw_torch_fused",  # beste performance mit H100
)

# Define Data Collator
def data_collator(features):
    batch = {}
    batch["input_ids"] = torch.nn.utils.rnn.pad_sequence(
        [torch.tensor(f["input_ids"], dtype=torch.long) for f in features],
        batch_first=True,
        padding_value=tokenizer.pad_token_id or 0  # robust falls pad_token fehlt
    )
    batch["attention_mask"] = torch.nn.utils.rnn.pad_sequence(
        [torch.tensor(f["attention_mask"], dtype=torch.long) for f in features],
        batch_first=True,
        padding_value=0
    )
    batch["labels"] = batch["input_ids"].clone()
    return batch

# Define Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset.with_format("torch"),
    eval_dataset=None,  # kein Validation Dataset (kann ergänzt werden)
    tokenizer=tokenizer,
    data_collator=data_collator,
)

# Run training
trainer.train()

# Save model + tokenizer
trainer.save_model(config["output_dir"])
tokenizer.save_pretrained(config["output_dir"])

print("✅ LoRA training completed and model saved.")
