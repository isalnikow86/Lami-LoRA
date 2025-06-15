
#!/bin/bash

accelerate launch --multi_gpu \
  scripts/train_lora_combined.py \
  --config configs/lora_combined_config.yaml
