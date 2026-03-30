from .loader import load_pricing, get_model
from .cost_models import cost_tokens, cost_audio_minutes, supports_audio

def interactive():
    pricing = load_pricing()
    print("OpenAI Economics Calculator (q to quit)")

    while True:
        model = input("Model name: ").strip()
        if model.lower() in {"q", "quit", "exit"}:
            break

        try:
            model_cfg = get_model(pricing, model)
        except KeyError as e:
            print(e)
            continue

        mode = input("Mode [tokens/audio]: ").strip().lower()

        if mode == "tokens":
            try:
                inp = int(input("Input tokens: ").strip())
                out = int(input("Output tokens: ").strip())
                tier = input("Tier [standard/batch/etc, blank=standard]: ").strip() or "standard"
                total = cost_tokens(model_cfg, inp, out, tier)
                print(f"Estimated cost: ${total:,.6f}\n")
            except Exception as e:
                print(f"Error: {e}\n")

        elif mode == "audio":
            if not supports_audio(model_cfg):
                print(f"Model '{model}' does not support audio-per-minute pricing.\n")
                continue

            try:
                minutes = float(input("Minutes of audio: ").strip())
                total = cost_audio_minutes(model_cfg, minutes)
                print(f"Estimated cost: ${total:,.6f}\n")
            except Exception as e:
                print(f"Error: {e}\n")

        else:
            print("Unknown mode. Use 'tokens' or 'audio'.\n")
