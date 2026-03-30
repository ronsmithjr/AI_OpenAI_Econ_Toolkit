from fastapi import FastAPI
from pydantic import BaseModel
from open_ai_econ.loader import load_pricing, get_model
from open_ai_econ.cost_models import cost_tokens, cost_audio_minutes, supports_audio
from open_ai_econ.monthly import monthly_cost_tokens, monthly_growth_projection

app = FastAPI(title="AI OpenAI Economics Toolkit API")

pricing = load_pricing()


class TokenRequest(BaseModel):
    model: str
    input_tokens: int
    output_tokens: int
    calls_per_day: int = 1
    tier: str = "standard"


class AudioRequest(BaseModel):
    model: str
    minutes: float
    calls_per_day: int = 1


class ProjectionRequest(BaseModel):
    model: str
    input_tokens: int
    output_tokens: int
    calls_per_day: int
    months: int = 12
    growth_rate: float = 0.10
    tier: str = "standard"


@app.get("/")
def root():
    return {"message": "AI OpenAI Economics Toolkit API is running"}


@app.post("/cost/tokens")
def cost_tokens_endpoint(req: TokenRequest):
    cfg = get_model(pricing, req.model)
    per_call = cost_tokens(cfg, req.input_tokens, req.output_tokens, req.tier)
    daily = per_call * req.calls_per_day
    monthly = daily * 30.437
    return {
        "model": req.model,
        "per_call": per_call,
        "daily_cost": daily,
        "monthly_cost": monthly,
    }


@app.post("/cost/audio")
def cost_audio_endpoint(req: AudioRequest):
    cfg = get_model(pricing, req.model)
    if not supports_audio(cfg):
        return {"error": f"Model '{req.model}' does not support audio pricing."}
    per_min = cost_audio_minutes(cfg, req.minutes)
    daily = per_min * req.calls_per_day
    monthly = daily * 30.437
    return {
        "model": req.model,
        "daily_cost": daily,
        "monthly_cost": monthly,
    }


@app.post("/projection")
def projection_endpoint(req: ProjectionRequest):
    cfg = get_model(pricing, req.model)
    base = monthly_cost_tokens(cfg, req.input_tokens, req.output_tokens, req.calls_per_day, req.tier)
    proj = monthly_growth_projection(
        cfg,
        req.input_tokens,
        req.output_tokens,
        req.calls_per_day,
        req.tier,
        req.months,
        req.growth_rate
    )
    return {
        "model": req.model,
        "base_month": base,
        "projection": proj,
    }
