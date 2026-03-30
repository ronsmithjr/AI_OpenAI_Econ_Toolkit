import streamlit as st
from open_ai_econ.loader import load_pricing, get_model
from open_ai_econ.cost_models import cost_tokens, supports_audio, cost_audio_minutes
from open_ai_econ.monthly import monthly_cost_tokens, monthly_growth_projection
from webui.scenario_loader import scenario_loader_ui

from open_ai_econ.html_dashboard import generate_dashboard
from open_ai_econ.html_dashboard_multi import generate_multi_model_dashboard
import streamlit.components.v1 as components

from urllib.parse import urlencode


st.title("AI OpenAI Economics Toolkit — Web UI")
st.set_page_config(layout="wide")

st.markdown("""
<style>
/* Remove top padding */
.main .block-container {
    padding-top: 0rem;
    padding-bottom: 0rem;
    max-width: 95%;
}

/* Force full-height layout */
html, body, [data-testid="stAppViewContainer"] {
    height: 100%;
    overflow: hidden;
}

/* Allow charts/tables to expand */
[data-testid="stVerticalBlock"] {
    height: 100%;
}
</style>
""", unsafe_allow_html=True)



pricing = load_pricing()
model_names = []

# Flatten model list
for section in pricing.values():
    if isinstance(section, dict):
        model_names.extend(section.keys())

model = st.selectbox("Model", sorted(model_names))
model_cfg = get_model(pricing, model)

mode = st.radio("Mode", ["Tokens", "Audio"])

if mode == "Tokens":
    input_tokens = st.number_input("Input tokens", min_value=0, value=1000)
    output_tokens = st.number_input("Output tokens", min_value=0, value=500)
    calls_per_day = st.number_input("Calls per day", min_value=1, value=1000)
    tier = st.text_input("Tier", value="standard")

    if st.button("Calculate"):
        base = monthly_cost_tokens(
            model_cfg, input_tokens, output_tokens, calls_per_day, tier
        )
        st.write(base)

        proj = monthly_growth_projection(
            model_cfg, input_tokens, output_tokens, calls_per_day
        )
        st.line_chart([p["monthly_cost"] for p in proj])

else:
    if not supports_audio(model_cfg):
        st.error("This model does not support audio-per-minute pricing.")
    else:
        minutes = st.number_input("Minutes per day", min_value=0.0, value=100.0)
        if st.button("Calculate"):
            cost = cost_audio_minutes(model_cfg, minutes)
            st.write({"daily_cost": cost, "monthly_cost": cost * 30.437})




page = st.sidebar.selectbox(
    "Navigation", ["Calculator", "Scenario Loader", "HTML Dashboard"]
)

if page == "Calculator":
    # your existing calculator UI
    ...
elif page == "Scenario Loader":
    scenario_loader_ui()
elif page == "HTML Dashboard":
    st.header("HTML Dashboard Generator")
    dashboard_type = st.radio("Dashboard Type", ["Single Model", "Multi Model"])
    if dashboard_type == "Single Model":
        model = st.selectbox("Model", sorted(model_names), key="html_model")
        model_cfg = get_model(pricing, model)
        input_tokens = st.number_input(
            "Input tokens", min_value=0, value=1000, key="html_input_tokens"
        )
        output_tokens = st.number_input(
            "Output tokens", min_value=0, value=500, key="html_output_tokens"
        )
        calls_per_day = st.number_input(
            "Calls per day", min_value=1, value=1000, key="html_calls_per_day"
        )
        tier = st.text_input("Tier", value="standard", key="html_tier")
        if st.button("Generate HTML Dashboard", key="html_single_btn"):
            html = generate_dashboard(
                model, model_cfg, input_tokens, output_tokens, calls_per_day, tier
            )
            components.html(html, height=900, scrolling=True)
    else:
        selected_models = st.multiselect(
            "Models",
            sorted(model_names),
            default=sorted(model_names)[:2],
            key="html_multi_models",
        )
        input_tokens = st.number_input(
            "Input tokens", min_value=0, value=1000, key="html_multi_input_tokens"
        )
        output_tokens = st.number_input(
            "Output tokens", min_value=0, value=500, key="html_multi_output_tokens"
        )
        calls_per_day = st.number_input(
            "Calls per day", min_value=1, value=1000, key="html_multi_calls_per_day"
        )
        tier = st.text_input("Tier", value="standard", key="html_multi_tier")
        if st.button("Generate Multi-Model HTML Dashboard", key="html_multi_btn"):
            models_dict = {name: get_model(pricing, name) for name in selected_models}
            html = generate_multi_model_dashboard(
                models_dict, input_tokens, output_tokens, calls_per_day, tier
            )
            components.html(html, height=1200, scrolling=True)


def scenario_deeplink(path: str):
    params = urlencode({"scenario": path})
    return f"http://localhost:8501/?{params}"
