
# 📘 PDF Export

The toolkit can convert any dashboard (single or multi‑model) into a PDF file.

PDF export uses **WeasyPrint**, a pure‑Python HTML → PDF engine.

---

## Generate a PDF

### Single model

```Powershell
open-ai-econ pdf \
  --models gpt-5.4 \
  --input-tokens 1200 \
  --output-tokens 400 \
  --calls-per-day 50000 \
  --out report.pdf

```

### Multimodel

```PowerShell
open-ai-econ pdf \
  --models gpt-5.4 gpt-5.4-mini \
  --input-tokens 1200 \
  --output-tokens 400 \
  --calls-per-day 50000 \
  --out comparison.pdf
```