import sys
import os
from datetime import datetime
import subprocess

import argparse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from open_ai_econ.calculator import interactive
from open_ai_econ.yaml_runner import run_yaml
from open_ai_econ.export import export_projection_to_csv
from open_ai_econ.charts import plot_monthly_projection
from open_ai_econ.compare import compare_models
from open_ai_econ.html_dashboard import generate_dashboard
from open_ai_econ.loader import load_pricing, get_model

from open_ai_econ.html_dashboard_multi import generate_multi_model_dashboard
import uvicorn
from open_ai_econ.api.fastapi_app import app

from open_ai_econ.html_dashboard import generate_dashboard
from open_ai_econ.html_dashboard_multi import generate_multi_model_dashboard
from webui.app import scenario_deeplink





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
    
    output_dir = os.path.join(os.path.dirname(args.out) or ".", "output")
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_safe = args.model.replace("/", "_").replace(" ", "_")
    base_name = f"dashboard_{model_safe}_{timestamp}.html"
    output_path = os.path.join(output_dir, base_name)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Dashboard written to {output_path}")

def _dashboard_multi_cmd(args):
    pricing = load_pricing()
    model_cfgs = {name: get_model(pricing, name) for name in args.models}

    html = generate_multi_model_dashboard(
        model_cfgs,
        args.input_tokens,
        args.output_tokens,
        args.calls_per_day,
        args.tier
    )

    output_dir = os.path.join(os.path.dirname(args.out) or ".", "output")
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = f"multi_dashboard_{timestamp}.html"
    output_path = os.path.join(output_dir, base_name)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Multi‑model dashboard written to {output_path}")

def _api_cmd(args):
    uvicorn.run(app, host=args.host, port=args.port)

def _pdf_cmd(args):
    pricing = load_pricing()
    model_cfgs = {name: get_model(pricing, name) for name in args.models}

    # Single model → use single dashboard
    if len(args.models) == 1:
        html = generate_dashboard(
            args.models[0],
            model_cfgs[args.models[0]],
            args.input_tokens,
            args.output_tokens,
            args.calls_per_day,
            args.tier
        )
    else:
        # Multi-model dashboard
        html = generate_multi_model_dashboard(
            model_cfgs,
            args.input_tokens,
            args.output_tokens,
            args.calls_per_day,
            args.tier
        )
def _webui_cmd(args):
    subprocess.run([sys.executable, "-m", "streamlit", "run", "webui/app.py"])

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

    pmulti = sub.add_parser("dashboard-multi", help="Generate multi-model HTML dashboard")
    pmulti.add_argument("--models", nargs="+", required=True)
    pmulti.add_argument("--input-tokens", type=int, required=True)
    pmulti.add_argument("--output-tokens", type=int, required=True)
    pmulti.add_argument("--calls-per-day", type=int, required=True)
    pmulti.add_argument("--tier", default="standard")
    pmulti.add_argument("--out", required=True)   

    pmulti.set_defaults(func=_dashboard_multi_cmd)

    papi = sub.add_parser("api", help="Run the REST API server")
    papi.add_argument("--host", default="127.0.0.1")
    papi.add_argument("--port", type=int, default=8000)
    papi.set_defaults(func=_api_cmd)

    ppdf = sub.add_parser("pdf", help="Generate a PDF from a dashboard")
    ppdf.add_argument("--models", nargs="+", required=True)
    ppdf.add_argument("--input-tokens", type=int, required=True)
    ppdf.add_argument("--output-tokens", type=int, required=True)
    ppdf.add_argument("--calls-per-day", type=int, required=True)
    ppdf.add_argument("--tier", default="standard")
    ppdf.add_argument("--out", required=True)
    ppdf.set_defaults(func=_pdf_cmd)

    pweb = sub.add_parser("webui", help="Launch the Streamlit Web UI")
    pweb.set_defaults(func=_webui_cmd)

    return p


def main():  

    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
