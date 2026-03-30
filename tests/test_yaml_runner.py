from open_ai_econ.yaml_runner import run_yaml
import tempfile
import yaml

def test_run_yaml_basic():
    scenario = {
        "model": "gpt-5.4",
        "tier": "standard",
        "usage": {
            "input_tokens": 1000,
            "output_tokens": 500,
            "calls_per_day": 1000
        }
    }

    with tempfile.NamedTemporaryFile("w", delete=False) as f:
        yaml.dump(scenario, f)
        f.flush()
        result = run_yaml(f.name)

    assert "base_month" in result
