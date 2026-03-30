import csv
from pathlib import Path

def export_projection_to_csv(rows, path):
    rows = list(rows)
    if not rows:
        return
    path = Path(path)
    fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
