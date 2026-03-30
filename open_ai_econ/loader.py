import json
from pathlib import Path

PRICING_PATH = Path(__file__).parent.parent / "pricing" / "pricing_openai.json"


def load_pricing():
    with open(PRICING_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_model(pricing, model_name):
    for section in pricing.values():
        if isinstance(section, dict) and model_name in section:
            return section[model_name]
    raise KeyError(f"Model '{model_name}' not found.")
