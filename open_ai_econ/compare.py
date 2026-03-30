from .loader import load_pricing, get_model
from .monthly import monthly_cost_tokens

def compare_models(models, input_tokens, output_tokens, calls_per_day, tier="standard"):
    pricing = load_pricing()
    results = []
    for name in models:
        cfg = get_model(pricing, name)
        info = monthly_cost_tokens(cfg, input_tokens, output_tokens, calls_per_day, tier)
        results.append({
            "model": name,
            "tier": tier,
            "per_call": info["per_call"],
            "daily_cost": info["daily_cost"],
            "monthly_cost": info["monthly_cost"],
        })
    return results
