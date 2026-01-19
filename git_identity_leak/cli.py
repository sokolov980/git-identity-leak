import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
from datetime import datetime

def plot_contributions_heatmap(signals, image_dir=None):
    daily = next(
        (s["value"] for s in signals if s["signal_type"] == "CONTRIBUTIONS_YEARLY_DATES"),
        None
    )

    if not daily:
        print("[!] No daily contributions found.")
        return

    daily = sorted(daily, key=lambda x: x["date"])

    start = datetime.strptime(daily[0]["date"], "%Y-%m-%d")
    end = datetime.strptime(daily[-1]["date"], "%Y-%m-%d")
    weeks = ((end - start).days // 7) + 1

    heatmap = np.zeros((7, weeks), dtype=int)

    for d in daily:
        dt = datetime.strptime(d["date"], "%Y-%m-%d")
        week = (dt - start).days // 7
        heatmap[dt.weekday(), week] = d["count"]

    plt.figure(figsize=(weeks / 2, 3))
    sns.heatmap(heatmap, cmap="Greens", cbar=True)
    plt.yticks(range(7), ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"], rotation=0)
    plt.xticks([])
    plt.title("GitHub Contributions")
    plt.tight_layout()

    if image_dir:
        os.makedirs(image_dir, exist_ok=True)
        path = os.path.join(image_dir, "contributions.png")
        plt.savefig(path, dpi=150)
        print(f"[+] Heatmap saved to {path}")
    else:
        plt.show()

    plt.close()
