#!/bin/bash
accelerate launch --multi_gpu \ scripts/train_lora.py \ --config configs/lora_config.yaml
