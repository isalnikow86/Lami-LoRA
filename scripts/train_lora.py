import os
import yaml
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments
from datasets import load_from_disk
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import BitsAndBytesConfig

# Load config
with open("configs/lora_config.yaml") as f:
    config = yaml.safe_load(f)


# Load model + tokenizer
model = AutoModelForCausalLM.from_pretrained(
    config["base_model"],
    device_map="auto",
    torch_dtype=torch.float16,
    load_in_8bit=False   # <== das ist der entscheidende Punkt!
)

tokenizer = AutoTokenizer.from_pretrained(config["base_model"])

# Ensure tokenizer has a pad_token
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

# Prepare model for k-bit training (8bit)
model = prepare_model_for_kbit_training(model)

# Setup LoRA config
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj"],  # bei LeoLM / LLaMA
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
)

# Apply LoRA
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()

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
    gradient_checkpointing=False,
    bf16=True,  # H100 optimal
    gradient_accumulation_steps=8,
    warmup_steps=100,
    weight_decay=0.01,
    optim="paged_adamw_8bit",  # wichtig für stability
    logging_dir="./logs",
)

# Define Data Collator
def data_collator(features):
    batch = {}
    batch["input_ids"] = torch.nn.utils.rnn.pad_sequence(
        [torch.tensor(f["input_ids"], dtype=torch.long) for f in features],
        batch_first=True,
        padding_value=tokenizer.pad_token_id,
    )
    batch["attention_mask"] = torch.nn.utils.rnn.pad_sequence(
        [torch.tensor(f["attention_mask"], dtype=torch.long) for f in features],
        batch_first=True,
        padding_value=0,
    )
    batch["labels"] = batch["input_ids"].clone()
    return batch

# Define Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset.with_format("torch"),
    eval_dataset=None,
    tokenizer=tokenizer,
    data_collator=data_collator,
)

# Run training
trainer.train()

# Save model + tokenizer
trainer.save_model(config["output_dir"])
tokenizer.save_pretrained(config["output_dir"])

print("LoRA training completed and model saved.")
