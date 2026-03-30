from .cost_models import cost_tokens

DAYS_PER_MONTH = 30.437

def monthly_cost_tokens(model_cfg, input_tokens, output_tokens, calls_per_day, tier="standard"):
    per_call = cost_tokens(model_cfg, input_tokens, output_tokens, tier)
    daily_cost = per_call * calls_per_day
    monthly_cost = daily_cost * DAYS_PER_MONTH

    return {
        "per_call": per_call,
        "daily_cost": daily_cost,
        "monthly_cost": monthly_cost,
        "calls_per_day": calls_per_day,
        "days": DAYS_PER_MONTH
    }


def monthly_growth_projection(
    model_cfg,
    input_tokens,
    output_tokens,
    calls_per_day,
    tier="standard",
    months=12,
    growth_rate=0.10,
):
    results = []
    current_calls = calls_per_day

    for month in range(1, months + 1):
        cost_info = monthly_cost_tokens(
            model_cfg,
            input_tokens,
            output_tokens,
            current_calls,
            tier
        )
        results.append({
            "month": month,
            "calls_per_day": current_calls,
            "monthly_cost": cost_info["monthly_cost"]
        })
        current_calls *= (1 + growth_rate)

    return results
