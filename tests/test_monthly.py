from open_ai_econ.monthly import monthly_cost_tokens

def test_monthly_cost_tokens():
    cfg = {"input": 10, "output": 20}
    result = monthly_cost_tokens(cfg, 1000, 500, 1000)
    assert "monthly_cost" in result
    assert result["monthly_cost"] > 0
