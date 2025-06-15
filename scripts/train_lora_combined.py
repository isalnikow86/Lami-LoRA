import os
import yaml
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments
from datasets import load_from_disk

# Load config
with open("configs/lora_combined_config.yaml") as f:
    config = yaml.safe_load(f)

# Load model + tokenizer
model = AutoModelForCausalLM.from_pretrained(
    config["base_model"],
    device_map="auto",
    trust_remote_code=True,
    torch_dtype=torch.float16
)
tokenizer = AutoTokenizer.from_pretrained(config["base_model"])
tokenizer.pad_token = tokenizer.eos_token  # falls nicht gesetzt

dataset = load_from_disk("data/tokenized_klexikon_dataset").select(range(500))


training_args = TrainingArguments(
    output_dir=config["output_dir"],
    learning_rate=float(config["learning_rate"]),
    per_device_train_batch_size=config["batch_size"],
    num_train_epochs=config["num_train_epochs"],
    logging_steps=config["logging_steps"],
    save_steps=config["save_steps"],
    gradient_checkpointing=True,     # ✅ reduziert RAM massiv
    bf16=True,
    fp16=False,
    optim="adamw_torch_fused",
    torch_compile=True               # ✅ optionaler Boost
)


# Define Data Collator
def data_collator(features):
    batch = {}
    batch["input_ids"] = torch.nn.utils.rnn.pad_sequence(
        [torch.tensor(f["input_ids"], dtype=torch.long) for f in features],
        batch_first=True,
        padding_value=tokenizer.pad_token_id or 0
    )
    batch["attention_mask"] = torch.nn.utils.rnn.pad_sequence(
        [torch.tensor(f["attention_mask"], dtype=torch.long) for f in features],
        batch_first=True,
        padding_value=0
    )
    batch["labels"] = batch["input_ids"].clone()
    return batch

# Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset.with_format("torch"),
    eval_dataset=None,
    tokenizer=tokenizer,
    data_collator=data_collator,
)

# Train
trainer.train()

# Save
trainer.save_model(config["output_dir"])
tokenizer.save_pretrained(config["output_dir"])

print("✅ LoRA training completed and model saved.")
