# git_identity_leak/cli.py

import argparse
import json
import os
from datetime import datetime

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from git_identity_leak.analysis import full_analysis
from git_identity_leak.graph import build_identity_graph, save_graph_json
from git_identity_leak.report import save_report

TRUNCATE_LEN = 120  # for console output


def pretty_print_signals(signals, truncate_len=TRUNCATE_LEN):
    print("[DEBUG] Signals:")
    if not signals:
        print("  No signals collected.")
        return

    headers = ["TYPE", "VALUE", "CONFIDENCE"]
    col_widths = [30, truncate_len, 10]
    divider = "-" * (sum(col_widths) + 4)

    print(divider)
    print(f"{headers[0]:<{col_widths[0]}} {headers[1]:<{col_widths[1]}} {headers[2]:<{col_widths[2]}}")
    print(divider)

    contrib_total = None
    contrib_pattern = None
    contrib_years = {}

    for s in signals:
        stype = s.get("signal_type", "UNKNOWN")
        value = str(s.get("value", ""))
        confidence = s.get("confidence", "")

        if stype == "CONTRIBUTION_TOTAL":
            contrib_total = value
            continue
        if stype == "CONTRIBUTION_TIME_PATTERN":
            contrib_pattern = value
            continue
        if stype == "CONTRIBUTIONS_YEAR":
            year = s.get("meta", {}).get("year", value)
            count = s.get("meta", {}).get("count", 0)
            contrib_years[year] = count
            continue

        display_value = value if len(value) <= truncate_len else value[:truncate_len - 3] + "..."
        print(f"{stype:<{col_widths[0]}} {display_value:<{col_widths[1]}} {confidence:<{col_widths[2]}}")

    if contrib_total:
        print(f"{'CONTRIBUTION_TOTAL':<{col_widths[0]}} {contrib_total:<{col_widths[1]}} HIGH")
    if contrib_pattern:
        print(f"{'CONTRIBUTION_TIME_PATTERN':<{col_widths[0]}} {contrib_pattern:<{col_widths[1]}} MEDIUM")
    for y in sorted(contrib_years):
        print(f"{'CONTRIBUTIONS_YEAR':<{col_widths[0]}} {y}: {contrib_years[y]:<{col_widths[1]}} HIGH")

    print(divider)


def plot_contributions_heatmap(signals, image_dir=None, username="github_user"):
    """
    GitHub-style weekly contributions heatmap
    """
    daily_signal = next(
        (s for s in signals if s["signal_type"] == "CONTRIBUTIONS_YEARLY_DATES"),
        None
    )

    if not daily_signal or not daily_signal.get("value"):
        print("[!] No daily contributions found, skipping heatmap.")
        return

    days = sorted(daily_signal["value"], key=lambda x: x["date"])
    first_date = datetime.strptime(days[0]["date"], "%Y-%m-%d")
    last_date = datetime.strptime(days[-1]["date"], "%Y-%m-%d")

    num_weeks = ((last_date - first_date).days // 7) + 1
    heatmap = np.zeros((7, num_weeks), dtype=int)

    for d in days:
        dt = datetime.strptime(d["date"], "%Y-%m-%d")
        week = (dt - first_date).days // 7
        weekday = dt.weekday()  # Monday = 0
        if 0 <= week < num_weeks:
            heatmap[weekday, week] = d["count"]

    plt.figure(figsize=(max(num_weeks / 2, 10), 3))
    sns.heatmap(
        heatmap,
        cmap="Greens",
        cbar=True,
        linewidths=0.3,
        linecolor="lightgray"
    )

    plt.yticks(
        np.arange(7) + 0.5,
        ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        rotation=0
    )
    plt.xticks([])
    plt.title("GitHub Contributions Heatmap")
    plt.tight_layout()

    if image_dir:
        os.makedirs(image_dir, exist_ok=True)
        path = os.path.join(image_dir, f"{username}_contrib_heatmap.png")
        plt.savefig(path, dpi=150, bbox_inches="tight")
        print(f"[+] Contribution heatmap saved to {path}")
    else:
        plt.show()

    plt.close()


def pretty_print_dict(title, d):
    print(f"[DEBUG] {title}:")
    if not d:
        print("  No data.")
        return
    print(json.dumps(d, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Git Identity Leak OSINT Tool")
    parser.add_argument("--username", required=True)
    parser.add_argument("--images", help="Directory to save images")
    parser.add_argument("--graph-output", help="Save graph JSON")
    parser.add_argument("--output", help="Save report JSON")
    parser.add_argument("--temporal", action="store_true")
    parser.add_argument("--stylometry", action="store_true")
    parser.add_argument("--verbose", action="store_true")

    args = parser.parse_args()

    signals, temporal_data, stylometry_data = full_analysis(
        username=args.username,
        image_dir=args.images,
        include_temporal=args.temporal,
        include_stylometry=args.stylometry
    )

    if args.verbose:
        pretty_print_signals(signals)
        pretty_print_dict("Temporal data", temporal_data)
        pretty_print_dict("Stylometry data", stylometry_data)

    graph = build_identity_graph(signals)
    if args.graph_output:
        save_graph_json(args.graph_output, graph)
        print(f"[+] Graph saved to {args.graph_output}")

    if args.output:
        save_report(args.output, signals, temporal_data, stylometry_data)
        print(f"[+] Report saved to {args.output}")

    if args.images:
        plot_contributions_heatmap(signals, args.images, args.username)


if __name__ == "__main__":
    main()
