import base64
import matplotlib.pyplot as plt
from io import BytesIO
from .monthly import monthly_cost_tokens, monthly_growth_projection

def _plot_to_base64(fig):
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")

def generate_dashboard(model_name, model_cfg, input_tokens, output_tokens, calls_per_day, tier="standard"):
    base = monthly_cost_tokens(model_cfg, input_tokens, output_tokens, calls_per_day, tier)
    proj = monthly_growth_projection(model_cfg, input_tokens, output_tokens, calls_per_day, tier)

    # Chart
    fig, ax = plt.subplots(figsize=(8, 4))
    months = [p["month"] for p in proj]
    costs = [p["monthly_cost"] for p in proj]
    ax.plot(months, costs, marker="o")
    ax.set_xlabel("Month")
    ax.set_ylabel("Monthly Cost (USD)")
    ax.set_title(f"Monthly Cost Projection — {model_name}")
    chart_b64 = _plot_to_base64(fig)
    plt.close(fig)

    # HTML
    html = f"""
    <html>
    <head>
        <title>Cost Dashboard — {model_name}</title>
        <style>
            body {{ font-family: Arial; margin: 40px; }}
            h1 {{ color: #333; }}
            table {{ border-collapse: collapse; width: 60%; }}
            th, td {{ border: 1px solid #ccc; padding: 8px; }}
        </style>
    </head>
    <body>
        <h1>Cost Dashboard — {model_name}</h1>

        <h2>Base Monthly Cost</h2>
        <table>
            <tr><th>Per Call</th><td>${base['per_call']:.6f}</td></tr>
            <tr><th>Daily Cost</th><td>${base['daily_cost']:.2f}</td></tr>
            <tr><th>Monthly Cost</th><td>${base['monthly_cost']:.2f}</td></tr>
        </table>

        <h2>Projection Chart</h2>
        <img src="data:image/png;base64,{chart_b64}" />

        <h2>Projection Data</h2>
        <table>
            <tr><th>Month</th><th>Calls/Day</th><th>Monthly Cost</th></tr>
            {''.join(f"<tr><td>{p['month']}</td><td>{p['calls_per_day']:.0f}</td><td>${p['monthly_cost']:.2f}</td></tr>" for p in proj)}
        </table>
    </body>
    </html>
    """

    return html
