from open_ai_econ.loader import load_pricing, get_model

def test_load_pricing():
    pricing = load_pricing()
    assert isinstance(pricing, dict)
    assert "flagship_models" in pricing or len(pricing) > 0

def test_get_model():
    pricing = load_pricing()
    # Pick any model you know exists in your JSON
    model = get_model(pricing, "gpt-5.4")
    assert isinstance(model, dict)
