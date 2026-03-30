#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import argparse
import json
from pathlib import Path
from typing import Dict, Any
from open_ai_econ.yaml_runner import run_yaml
from open_ai_econ.export import export_projection_to_csv
from open_ai_econ.charts import plot_monthly_projection
from open_ai_econ.compare import compare_models



PRICING_PATH = Path(__file__).parent.parent / "pricing" / "pricing_openai.json"


# ---------- Core pricing loader ----------

def load_pricing() -> Dict[str, Any]:
    with open(PRICING_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_model_pricing(pricing: Dict[str, Any], model_name: str) -> Dict[str, Any]:
    # Flatten model lookup across sections
    for section in pricing.values():
        if isinstance(section, dict):
            if model_name in section:
                return section[model_name]
    raise ValueError(f"Model '{model_name}' not found in pricing JSON.")


# ---------- Cost primitives ----------

def cost_tokens(model_cfg: Dict[str, Any], input_tokens: int, output_tokens: int,
                tier: str = "standard") -> float:
    """
    Assumes prices are in USD per 1M tokens.
    model_cfg[tier] = { "input": ..., "output": ..., "cached_input": ...? }
    """
    tier_cfg = model_cfg.get(tier, model_cfg)  # allow flat or tiered
    in_rate = tier_cfg.get("input", 0.0) / 1_000_000
    out_rate = tier_cfg.get("output", 0.0) / 1_000_000

    return input_tokens * in_rate + output_tokens * out_rate


def cost_audio_minutes(model_cfg: Dict[str, Any], minutes: float) -> float:
    """
    For transcription models where pricing is per 1M tokens but you’ve
    pre‑computed an estimated cost per minute in the JSON.
    """
    per_min = model_cfg.get("estimated_cost_per_minute")
    if per_min is None:
        raise ValueError("Model does not define 'estimated_cost_per_minute'.")
    return minutes * per_min


# ---------- Commands ----------

def cmd_estimate(args: argparse.Namespace) -> None:
    pricing = load_pricing()
    model_cfg = get_model_pricing(pricing, args.model)

    if args.mode == "tokens":
        total = cost_tokens(
            model_cfg,
            input_tokens=args.input_tokens,
            output_tokens=args.output_tokens,
            tier=args.tier,
        )
        print(f"Estimated cost: ${total:,.6f}")
    elif args.mode == "audio":
        total = cost_audio_minutes(model_cfg, minutes=args.minutes)
        print(f"Estimated cost: ${total:,.6f}")
    else:
        raise ValueError(f"Unknown mode: {args.mode}")


def cmd_scenario(args: argparse.Namespace) -> None:
    """
    Simple scenario modeling:
    - N calls
    - each with given input/output tokens
    - optional scale factor
    """
    pricing = load_pricing()
    model_cfg = get_model_pricing(pricing, args.model)

    per_call = cost_tokens(
        model_cfg,
        input_tokens=args.input_tokens,
        output_tokens=args.output_tokens,
        tier=args.tier,
    )
    total_calls = args.calls * args.scale
    total_cost = per_call * total_calls

    print(f"Model: {args.model}")
    print(f"Tier: {args.tier}")
    print(f"Per‑call cost: ${per_call:,.6f}")
    print(f"Total calls: {total_calls:,}")
    print(f"Scenario total: ${total_cost:,.6f}")


def cmd_calculator(_: argparse.Namespace) -> None:
    """
    Interactive loop: quick what‑if calculator.
    """
    pricing = load_pricing()

    print("OpenAI Economics Calculator (q to quit)")
    while True:
        model = input("Model name: ").strip()
        if model.lower() in {"q", "quit", "exit"}:
            break

        try:
            model_cfg = get_model_pricing(pricing, model)
        except ValueError as e:
            print(e)
            continue

        mode = input("Mode [tokens/audio]: ").strip().lower()
        if mode == "tokens":
            try:
                inp = int(input("Input tokens: ").strip())
                out = int(input("Output tokens: ").strip())
                tier = input("Tier [standard/batch/etc, blank=standard]: ").strip() or "standard"
                total = cost_tokens(model_cfg, inp, out, tier=tier)
                print(f"Estimated cost: ${total:,.6f}\n")
            except Exception as e:
                print(f"Error: {e}\n")
        elif mode == "audio":
            try:
                minutes = float(input("Minutes of audio: ").strip())
                total = cost_audio_minutes(model_cfg, minutes)
                print(f"Estimated cost: ${total:,.6f}\n")
            except Exception as e:
                print(f"Error: {e}\n")
        else:
            print("Unknown mode. Use 'tokens' or 'audio'.\n")

def _run_yaml_cmd(args):
       result = run_yaml(args.file)
       base = result["base_month"]
       print(f"Base monthly cost: ${base['monthly_cost']:,.2f}")
       proj = result.get("projection")
       if proj:
           if args.csv:
               export_projection_to_csv(proj, args.csv)
               print(f"Projection exported to {args.csv}")
           if args.plot:
               plot_monthly_projection(proj, title=f"Scenario: {args.file}")
       else:
           print("No projection section in scenario.")

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

# ---------- CLI wiring ----------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="OpenAI Economics Toolkit CLI — cost estimates & scenario modeling"
    )
    sub = p.add_subparsers(dest="command", required=True)

    # estimate
    pe = sub.add_parser("estimate", help="Estimate cost for a single usage pattern")
    pe.add_argument("--model", required=True, help="Model name as in pricing JSON")
    pe.add_argument("--mode", choices=["tokens", "audio"], default="tokens")
    pe.add_argument("--tier", default="standard", help="Pricing tier key (e.g., standard, batch)")
    pe.add_argument("--input-tokens", type=int, default=0, help="Input tokens (for tokens mode)")
    pe.add_argument("--output-tokens", type=int, default=0, help="Output tokens (for tokens mode)")
    pe.add_argument("--minutes", type=float, default=0.0, help="Audio minutes (for audio mode)")
    pe.set_defaults(func=cmd_estimate)

    # scenario
    # ps = sub.add_parser("scenario", help="Scenario modeling over many calls")
    # ps.add_argument("--model", required=True)
    # ps.add_argument("--tier", default="standard")
    # ps.add_argument("--input-tokens", type=int, required=True)
    # ps.add_argument("--output-tokens", type=int, required=True)
    # ps.add_argument("--calls", type=int, required=True, help="Base number of calls")
    # ps.add_argument("--scale", type=int, default=1, help="Scale factor (e.g., 10x traffic)")
    # ps.set_defaults(func=cmd_scenario)

    # calculator
    pc = sub.add_parser("calculator", help="Interactive what‑if calculator")
    pc.set_defaults(func=cmd_calculator)

    #yaml scenarios
    # ps = sub.add_parser("run", help="Run a YAML scenario file")
    # ps.add_argument("file", help="Path to scenario YAML")
    # ps.set_defaults(func=lambda args: print(run_yaml(args.file)))

    pr = sub.add_parser("run", help="Run a YAML scenario file")
    pr.add_argument("file")
    pr.add_argument("--csv")
    pr.add_argument("--plot", action="store_true")

   

    pr.set_defaults(func=_run_yaml_cmd)


    pcmp = sub.add_parser("compare", help="Compare monthly cost across models")
    pcmp.add_argument("--models", nargs="+", required=True)
    pcmp.add_argument("--input-tokens", type=int, required=True)
    pcmp.add_argument("--output-tokens", type=int, required=True)
    pcmp.add_argument("--calls-per-day", type=int, required=True)
    pcmp.add_argument("--tier", default="standard")

    

    pcmp.set_defaults(func=_compare_cmd)



    return p


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
