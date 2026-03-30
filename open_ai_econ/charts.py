import matplotlib.pyplot as plt

def plot_monthly_projection(rows, title=None):
    months = [r["month"] for r in rows]
    costs = [r["monthly_cost"] for r in rows]

    plt.figure(figsize=(8, 4))
    plt.plot(months, costs, marker="o")
    plt.xlabel("Month")
    plt.ylabel("Monthly cost (USD)")
    if title:
        plt.title(title)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()
