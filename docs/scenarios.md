
### `docs/scenarios.md`

```markdown
# Scenario Files
```

Example:

```yaml
model: gpt-5.4
tier: standard
usage:
  input_tokens: 1200
  output_tokens: 400
  calls_per_day: 50000
projection:
  months: 12
  growth_rate: 0.08
```

This gives you a full documentation site ready for GitHub Pages.

---

# 🎨 3. Logo / Branding  
You want something simple, clean, and developer‑friendly.

Here are **three branding directions** you can choose from:

### **Option A — Minimalist Token Stack**
- Three stacked rectangles (tokens)
- Blue → Purple gradient
- “Econ Toolkit” underneath

### **Option B — AI Circuit + Dollar Sign**

- Circuit lines forming a subtle “$”
- Clean geometric style
- Works well as a favicon

### **Option C — Bar Chart + Neural Node**

- Rising bars (cost modeling)
- Node/connection overlay (AI)
- Very “engineering‑toolkit” vibe

Pick one and I’ll generate:

- SVG
- PNG
- Dark/light variants
- Favicon version
- README badge

---

# 📦 4. Scenario Pack (Common Workloads)

Create:
scenarios/
basic_usage.yaml
growth_projection.yaml
customer_support.yaml
rag_pipeline.yaml
agentic_automation.yaml
batch_processing.yaml
stt_pipeline.yaml



### `scenarios/customer_support.yaml`

```yaml
model: gpt-5.4-mini
tier: standard

usage:
  input_tokens: 900
  output_tokens: 300
  calls_per_day: 150000

projection:
  months: 12
  growth_rate: 0.05
```