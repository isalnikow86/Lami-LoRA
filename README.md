Lami-LoRA - Fine-Tuning LeoLM-7B with Klexikon Data
This repository contains scripts to fine-tune the LeoLM/leo-hessianai-7b model using articles from Klexikon (children-friendly Wikipedia).

🚀 Workflow
1️⃣ Prepare the Dataset (Tokenization)
Run once to convert your klexikon_texts.jsonl into a tokenized dataset:

python3 scripts/prepare_lora_data.py

This will create data/tokenized_klexikon_dataset.

2️⃣ Run LoRA Training
Recommended GPU: H100 (batch_size 1-4).

Set memory fragmentation workaround:
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:128

Then start training:
python3 scripts/train_lora.py --config configs/lora_config.yaml

Progress and checkpoints will be written to:
lora-outputs/

3️⃣ Result
The folder lora-outputs/ will contain:

-LoRA fine-tuned weights
-Updated tokenizer

⚙️ Configuration
Edit hyperparameters in configs/lora_config.yaml:
base_model: LeoLM/leo-hessianai-7b
output_dir: lora-outputs/
learning_rate: 5e-5
batch_size: 1
num_train_epochs: 3
logging_steps: 10
save_steps: 100

ℹ️ Notes
-For large models (7B), gradient_checkpointing=False (safe on H100)
-If you get cublasLt errors → lower batch_size or adjust max_split_size_mb.
-Use torch_dtype=torch.float16 for best H100 stability.

✅ Tested with
LeoLM/leo-hessianai-7b (H100 GPU)

-PyTorch 2.1+
-Transformers 4.41
-BitsAndBytes 0.41
-PEFT 0.11.1
-Datasets 2.19

🔄 Full Training Cycle
1️⃣ Prepare dataset:
python3 scripts/prepare_lora_data.py

2️⃣ Train LoRA:

export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:128
python3 scripts/train_lora.py --config configs/lora_config.yaml

🚀 Summary
LoRA training pipeline for LeoLM-7B with German children's content (Klexikon).

-Efficient fine-tuning via LoRA
-Tested on H100 GPUs
-Production-ready setup
-Modular / reusable






