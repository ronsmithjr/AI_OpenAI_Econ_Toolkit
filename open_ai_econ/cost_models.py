def cost_tokens(model_cfg, input_tokens, output_tokens, tier="standard"):
    tier_cfg = model_cfg.get(tier, model_cfg)
    in_rate = tier_cfg.get("input", 0) / 1_000_000
    out_rate = tier_cfg.get("output", 0) / 1_000_000
    return input_tokens * in_rate + output_tokens * out_rate


def cost_audio_minutes(model_cfg, minutes):
    per_min = model_cfg.get("estimated_cost_per_minute")
    if per_min is None:
        raise ValueError("Model does not define 'estimated_cost_per_minute'.")
    return minutes * per_min


def supports_audio(model_cfg):
    return "estimated_cost_per_minute" in model_cfg
