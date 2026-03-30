import yaml
from .loader import load_pricing, get_model
from .monthly import monthly_cost_tokens, monthly_growth_projection
from .cost_models import supports_audio

def run_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    pricing = load_pricing()
    model_cfg = get_model(pricing, cfg["model"])

    usage = cfg["usage"]
    projection = cfg.get("projection")

    # If YAML tries to use audio pricing on a model that doesn't support it
    if usage.get("mode") == "audio" and not supports_audio(model_cfg):
        raise ValueError(f"Model '{cfg['model']}' does not support audio-per-minute pricing.")

    base = monthly_cost_tokens(
        model_cfg,
        usage["input_tokens"],
        usage["output_tokens"],
        usage["calls_per_day"],
        cfg.get("tier", "standard")
    )

    result = {"base_month": base}

    if projection:
        result["projection"] = monthly_growth_projection(
            model_cfg,
            usage["input_tokens"],
            usage["output_tokens"],
            usage["calls_per_day"],
            cfg.get("tier", "standard"),
            projection.get("months", 12),
            projection.get("growth_rate", 0.10)
        )

    return result
