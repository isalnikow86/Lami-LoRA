#!/bin/bash

export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:32

accelerate launch --config_file ~/.cache/huggingface/accelerate/default_config.yaml \
  scripts/train_lora_combined.py --config configs/lora_combined_config.yaml
