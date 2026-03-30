import streamlit as st
import yaml
from pathlib import Path

from open_ai_econ.loader import load_pricing, get_model
from open_ai_econ.monthly import monthly_cost_tokens, monthly_growth_projection
from open_ai_econ.cost_models import supports_audio, cost_audio_minutes


SCENARIO_DIR = Path("scenarios")


def load_yaml_file(file):
    return yaml.safe_load(file.read())


def load_yaml_path(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def run_scenario(cfg):
    pricing = load_pricing()
    model_cfg = get_model(pricing, cfg["model"])

    usage = cfg["usage"]
    tier = cfg.get("tier", "standard")

    # Audio mode
    if usage.get("mode") == "audio":
        if not supports_audio(model_cfg):
            st.error(f"Model '{cfg['model']}' does not support audio pricing.")
            return None

        minutes = usage["minutes_per_day"]
        daily_cost = cost_audio_minutes(model_cfg, minutes)
        monthly_cost = daily_cost * 30.437

        return {
            "base_month": {
                "per_call": None,
                "daily_cost": daily_cost,
                "monthly_cost": monthly_cost,
            },
            "projection": None,
        }

    # Token mode
    base = monthly_cost_tokens(
        model_cfg,
        usage["input_tokens"],
        usage["output_tokens"],
        usage["calls_per_day"],
        tier,
    )

    proj_cfg = cfg.get("projection")
    projection = None

    if proj_cfg:
        projection = monthly_growth_projection(
            model_cfg,
            usage["input_tokens"],
            usage["output_tokens"],
            usage["calls_per_day"],
            tier,
            proj_cfg.get("months", 12),
            proj_cfg.get("growth_rate", 0.10),
        )

    return {"base_month": base, "projection": projection}


def scenario_loader_ui():
    st.header("Scenario Loader")

    st.write("### Load a scenario from file OR choose from the scenarios folder.")

    # --- Option A: Upload YAML ---
    uploaded = st.file_uploader("Upload a scenario (.yaml)", type=["yaml", "yml"])

    # --- Option B: Browse scenarios folder ---
    scenario_files = sorted(SCENARIO_DIR.glob("*.yaml"))
    selected = st.selectbox(
        "Or choose a scenario from the scenarios/ folder",
        ["(none)"] + [f.name for f in scenario_files],
    )

    cfg = None

    if uploaded:
        st.success("Loaded scenario from uploaded file.")
        cfg = load_yaml_file(uploaded)

    elif selected != "(none)":
        st.success(f"Loaded scenario: {selected}")
        cfg = load_yaml_path(SCENARIO_DIR / selected)

    if cfg:
        st.write("### Scenario Configuration")
        st.json(cfg)

        if st.button("Run Scenario"):
            result = run_scenario(cfg)
            if result:
                base = result["base_month"]
                st.write("### Base Monthly Cost")
                st.write(base)

                proj = result["projection"]
                if proj:
                    st.write("### Projection Table")
                    st.dataframe(proj)

                    st.write("### Projection Chart")
                    st.line_chart([p["monthly_cost"] for p in proj])
