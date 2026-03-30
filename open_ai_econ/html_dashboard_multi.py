import base64
import matplotlib.pyplot as plt
from io import BytesIO
from .monthly import monthly_cost_tokens, monthly_growth_projection


def _plot_to_base64(fig):
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


def generate_multi_model_dashboard(
    models: dict,
    input_tokens: int,
    output_tokens: int,
    calls_per_day: int,
    tier: str = "standard"
):
    """
    models: dict of {model_name: model_cfg}
    """

    # Compute economics for each model
    results = {}
    charts = {}

    for name, cfg in models.items():
        base = monthly_cost_tokens(cfg, input_tokens, output_tokens, calls_per_day, tier)
        proj = monthly_growth_projection(cfg, input_tokens, output_tokens, calls_per_day, tier)
        results[name] = {"base": base, "proj": proj}

        # Chart
        fig, ax = plt.subplots(figsize=(6, 3))
        months = [p["month"] for p in proj]
        costs = [p["monthly_cost"] for p in proj]
        ax.plot(months, costs, marker="o")
        ax.set_xlabel("Month")
        ax.set_ylabel("Monthly Cost (USD)")
        ax.set_title(f"{name} — Monthly Projection")
        charts[name] = _plot_to_base64(fig)
        plt.close(fig)

    # Build comparison table rows
    table_rows = ""
    for name, data in results.items():
        base = data["base"]
        table_rows += f"""
        <tr>
            <td>{name}</td>
            <td>${base['per_call']:.6f}</td>
            <td>${base['daily_cost']:.2f}</td>
            <td>${base['monthly_cost']:.2f}</td>
        </tr>
        """

    # Build individual model sections
    model_sections = ""
    for name, data in results.items():
        base = data["base"]
        proj = data["proj"]
        chart_b64 = charts[name]

        proj_rows = "".join(
            f"<tr><td>{p['month']}</td><td>{p['calls_per_day']:.0f}</td><td>${p['monthly_cost']:.2f}</td></tr>"
            for p in proj
        )

        model_sections += f"""
        <h2>{name}</h2>
        <table>
            <tr><th>Per Call</th><td>${base['per_call']:.6f}</td></tr>
            <tr><th>Daily Cost</th><td>${base['daily_cost']:.2f}</td></tr>
            <tr><th>Monthly Cost</th><td>${base['monthly_cost']:.2f}</td></tr>
        </table>

        <img src="data:image/png;base64,{chart_b64}" />

        <h3>Projection Data</h3>
        <table>
            <tr><th>Month</th><th>Calls/Day</th><th>Monthly Cost</th></tr>
            {proj_rows}
        </table>
        <hr>
        """

    # Final HTML
    html = f"""
    <html>
    <head>
        <title>Multi-Model Cost Dashboard</title>
        <style>
            body {{ font-family: Arial; margin: 40px; }}
            h1 {{ color: #333; }}
            table {{ border-collapse: collapse; width: 80%; margin-bottom: 30px; }}
            th, td {{ border: 1px solid #ccc; padding: 8px; }}
            th {{ background: #f0f0f0; }}
        </style>
    </head>
    <body>

        <h1>Multi-Model Cost Dashboard</h1>

        <h2>Comparison</h2>
        <table>
            <tr>
                <th>Model</th>
                <th>Per Call</th>
                <th>Daily Cost</th>
                <th>Monthly Cost</th>
            </tr>
            {table_rows}
        </table>

        {model_sections}

    </body>
    </html>
    """

    return html
