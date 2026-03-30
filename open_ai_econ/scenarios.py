from .cost_models import cost_tokens

def scenario_token_usage(model_cfg, input_tokens, output_tokens, calls, tier="standard"):
    per_call = cost_tokens(model_cfg, input_tokens, output_tokens, tier)
    return {
        "per_call": per_call,
        "calls": calls,
        "total_cost": per_call * calls
    }
