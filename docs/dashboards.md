# Dashboards

The toolkit supports two types of dashboards:

- **Single‑model dashboard**
- **Multi‑model dashboard (side‑by‑side comparison)**

Both dashboards are generated as standalone HTML files.

---

## Single‑Model Dashboard

```powershell
econ dashboard \
  --model gpt-5.4 \
  --input-tokens 1200 \
  --output-tokens 400 \
  --calls-per-day 50000 \
  --out dashboard.html
```

This produces:

Per‑call cost

Daily cost

Monthly cost

Growth projection chart

Projection table

## Multi‑Model Dashboard

```Powershell
econ dashboard-multi \
  --models gpt-5.4 gpt-5.4-mini gpt-5.4-pro \
  --input-tokens 1200 \
  --output-tokens 400 \
  --calls-per-day 50000 \
  --out multi_dashboard.html
```
This produces:

Side‑by‑side comparison table

Individual model sections

One chart per model

Projection tables



---
