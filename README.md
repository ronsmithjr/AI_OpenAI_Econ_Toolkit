# AI_OpenAI_Econ_Toolkit

### Disclaimer:  90% of this code was generated using AI

A modular, installable Python toolkit for modeling OpenAI API economics:

- Cost estimation
- Scenario modeling
- Monthly projections
- Growth curves
- YAML-driven workflows
- CLI tools
- CSV export
- Charts
- Multi-model comparison

---

## 📦 Installation

```PowerShell
pip install -e .
```

## 🚀 CLI Usage

### Interactive Calculator

```PowerShell
econ calculator
```

### Single Estimate

```PowerShell
econ estimate   --model gpt-5.4   --input-tokens 8000   --output-tokens 2000
```

### Run a YAML Scenario

```PowerShell
econ run scenarios/basic_usage.yaml
```

### With CSV export:

```PowerShell
econ run scenarios/growth_projection.yaml --csv out.csv
```

### With chart:

```PowerShell
econ run scenarios/growth_projection.yaml --plot
```

### Compare Models

```PowerShell
econ compare   --models gpt-5.4 gpt-5.4-mini gpt-5.4-pro   --input-tokens 1200   --output-tokens 400   --calls-per-day 50000
```

### 🧪 Running Tests

```PowerShell
pytest
```

## 📁 Project Structure

```text
open_ai_econ/
    loader.py
    cost_models.py
    monthly.py
    yaml_runner.py
    export.py
    charts.py
    compare.py
    pricing/openai_pricing.json

cli/
    cli.py

scenarios/
    basic_usage.yaml
    growth_projection.yaml

tests/
    test_loader.py
    test_cost_models.py
    test_monthly.py
    test_yaml_runner.py

```
