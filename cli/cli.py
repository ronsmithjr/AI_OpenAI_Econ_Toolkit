import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from open_ai_econ.calculator import interactive
from open_ai_econ.yaml_runner import run_yaml
from open_ai_econ.export import export_projection_to_csv
from open_ai_econ.charts import plot_monthly_projection
from open_ai_econ.compare import compare_models
from open_ai_econ.html_dashboard import generate_dashboard
from open_ai_econ.loader import load_pricing, get_model


import argparse


def _run_yaml_cmd(args):
    result = run_yaml(args.file)
    base = result["base_month"]
    print(f"Base monthly cost: ${base['monthly_cost']:,.2f}")

    proj = result.get("projection")
    if proj:
        if args.csv:
            export_projection_to_csv(proj, args.csv)
            print(f"Exported CSV → {args.csv}")
        if args.plot:
            plot_monthly_projection(proj, title=f"Scenario: {args.file}")


def _compare_cmd(args):
    rows = compare_models(
        args.models,
        args.input_tokens,
        args.output_tokens,
        args.calls_per_day,
        args.tier,
    )
    for r in rows:
        print(
            f"{r['model']} ({r['tier']}): "
            f"per_call=${r['per_call']:.6f}, "
            f"daily=${r['daily_cost']:.2f}, "
            f"monthly=${r['monthly_cost']:.2f}"
        )

def _dashboard_cmd(args):
    pricing = load_pricing()
    model_cfg = get_model(pricing, args.model)
    html = generate_dashboard(
        args.model,
        model_cfg,
        args.input_tokens,
        args.output_tokens,
        args.calls_per_day,
        args.tier,
    )
    import os
    from datetime import datetime
    output_dir = os.path.join(os.path.dirname(args.out) or ".", "output")
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_safe = args.model.replace("/", "_").replace(" ", "_")
    base_name = f"dashboard_{model_safe}_{timestamp}.html"
    output_path = os.path.join(output_dir, base_name)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Dashboard written to {output_path}")

def build_parser():
    p = argparse.ArgumentParser(description="OpenAI Economics Toolkit CLI")
    sub = p.add_subparsers(dest="command", required=True)

    # calculator
    pc = sub.add_parser("calculator", help="Interactive calculator")
    pc.set_defaults(func=lambda args: interactive())

    # YAML scenario
    pr = sub.add_parser("run", help="Run a YAML scenario file")
    pr.add_argument("file")
    pr.add_argument("--csv")
    pr.add_argument("--plot", action="store_true")

    pr.set_defaults(func=_run_yaml_cmd)

    # model comparison
    pcmp = sub.add_parser("compare", help="Compare monthly cost across models")
    pcmp.add_argument("--models", nargs="+", required=True)
    pcmp.add_argument("--input-tokens", type=int, required=True)
    pcmp.add_argument("--output-tokens", type=int, required=True)
    pcmp.add_argument("--calls-per-day", type=int, required=True)
    pcmp.add_argument("--tier", default="standard")

    pcmp.set_defaults(func=_compare_cmd)

    pdash = sub.add_parser("dashboard", help="Generate HTML cost dashboard")
    pdash.add_argument("--model", required=True)
    pdash.add_argument("--input-tokens", type=int, required=True)
    pdash.add_argument("--output-tokens", type=int, required=True)
    pdash.add_argument("--calls-per-day", type=int, required=True)
    pdash.add_argument("--tier", default="standard")
    pdash.add_argument("--out", required=True)

    

    pdash.set_defaults(func=_dashboard_cmd)

    return p


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
