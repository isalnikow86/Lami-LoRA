# Lami-LoRA
LoRA-Training-Projekt für LeoLM 7B GGUF auf Basis kindgerechter deutscher Texte.
## Struktur
- `klexikon_scraper.py` → lädt Klexikon Texte herunter - `data/klexikon_texts.jsonl` → gespeicherte Texte - 
`scripts/prepare_lora_data.py` → bereitet Dataset für Training vor - `scripts/train_lora.sh` → startet das Training - 
`configs/lora_config.yaml` → Konfiguration für das Training - `requirements.txt` → benötigte Python Libraries
## Workflow
1. Klexikon Texte laden: ```bash python klexikon_scraper.py
