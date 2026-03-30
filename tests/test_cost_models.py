from open_ai_econ.cost_models import cost_tokens, supports_audio

def test_cost_tokens():
    cfg = {"input": 10, "output": 20}
    cost = cost_tokens(cfg, 1000, 500)
    assert cost > 0

def test_supports_audio():
    assert supports_audio({"estimated_cost_per_minute": 0.01})
    assert not supports_audio({})
