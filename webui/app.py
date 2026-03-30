import streamlit as st
from open_ai_econ.loader import load_pricing, get_model
from open_ai_econ.cost_models import cost_tokens, supports_audio, cost_audio_minutes
from open_ai_econ.monthly import monthly_cost_tokens, monthly_growth_projection

st.title("AI OpenAI Economics Toolkit — Web UI")

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
        base = monthly_cost_tokens(model_cfg, input_tokens, output_tokens, calls_per_day, tier)
        st.write(base)

        proj = monthly_growth_projection(model_cfg, input_tokens, output_tokens, calls_per_day)
        st.line_chart([p["monthly_cost"] for p in proj])

else:
    if not supports_audio(model_cfg):
        st.error("This model does not support audio-per-minute pricing.")
    else:
        minutes = st.number_input("Minutes per day", min_value=0.0, value=100.0)
        if st.button("Calculate"):
            cost = cost_audio_minutes(model_cfg, minutes)
            st.write({"daily_cost": cost, "monthly_cost": cost * 30.437})
