# git_identity_leak/cli.py

import argparse
import json
import os
from datetime import datetime

from git_identity_leak.analysis import full_analysis
from git_identity_leak.graph import build_identity_graph, save_graph_json
from git_identity_leak.report import save_report

# plotting
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

TRUNCATE_LEN = 120

def pretty_print_signals(signals):
    print("\n[DEBUG] Signals:")
    if not signals:
        print("No signals collected.")
        return

    headers = ["TYPE", "VALUE", "CONFIDENCE"]
    widths = [30, TRUNCATE_LEN, 10]
    line = "-" * (sum(widths) + 4)

    print(line)
    print(f"{headers[0]:<{widths[0]}} {headers[1]:<{widths[1]}} {headers[2]:<{widths[2]}}")
    print(line)

    contrib_total = None
    contrib_pattern = None
    contrib_years = {}
    extra_info = []

    for s in signals:
        stype = s.get("signal_type", "")
        value = str(s.get("value", ""))
        conf = s.get("confidence", "")

        if stype == "CONTRIBUTION_TOTAL":
            contrib_total = value
            continue
        elif stype == "CONTRIBUTION_TIME_PATTERN":
            contrib_pattern = value
            continue
        elif stype == "CONTRIBUTIONS_YEAR":
            year = s.get("meta", {}).get("year", value)
            count = s.get("meta", {}).get("count", 0)
            contrib_years[year] = count
            continue
        elif stype in ("GITHUB_PAGES", "PRONOUNS", "PROFILE_PLATFORM"):
            extra_info.append((stype, value, conf))
            continue

        # Truncate long values
        if len(value) > TRUNCATE_LEN:
            value = value[:TRUNCATE_LEN - 3] + "..."

        print(f"{stype:<{widths[0]}} {value:<{widths[1]}} {conf:<{widths[2]}}")

    # Print contributions at the end
    if contrib_total:
        print(f"{'CONTRIBUTION_TOTAL':<{widths[0]}} {contrib_total:<{widths[1]}} HIGH")
    if contrib_pattern:
        print(f"{'CONTRIBUTION_TIME_PATTERN':<{widths[0]}} {contrib_pattern:<{widths[1]}} MEDIUM")
    for year in sorted(contrib_years.keys()):
        print(f"{'CONTRIBUTIONS_YEAR':<{widths[0]}} {year}: {contrib_years[year]:<{widths[1]}} HIGH")
    for stype, value, conf in extra_info:
        display_value = value if len(value) <= TRUNCATE_LEN else value[:TRUNCATE_LEN - 3] + "..."
        print(f"{stype:<{widths[0]}} {display_value:<{widths[1]}} {conf:<{widths[2]}}")

    print(line)


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
    sns.heatmap(heatmap, cmap="Greens", cbar=True, linewidths=0.5)
    plt.yticks(range(7), ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"], rotation=0)
    plt.xticks([])
    plt.title("GitHub Contributions")
    plt.tight_layout()

    if image_dir:
        os.makedirs(image_dir, exist_ok=True)
        path = os.path.join(image_dir, "contributions_heatmap.png")
        plt.savefig(path, dpi=150)
        print(f"[+] Heatmap saved to {path}")
    else:
        plt.show()
    plt.close()


def main():
    parser = argparse.ArgumentParser(description="Git Identity Leak OSINT Tool")

    # Old full-feature flags
    parser.add_argument("--username", required=True, help="GitHub username")
    parser.add_argument("--check-username", action="store_true", help="Check username validity")
    parser.add_argument("--check-email", action="store_true", help="Check email leaks")
    parser.add_argument("--check-posts", action="store_true", help="Check social posts")
    parser.add_argument("--temporal", action="store_true", help="Include temporal analysis")
    parser.add_argument("--stylometry", action="store_true", help="Include stylometry analysis")

    parser.add_argument("--images", help="Directory to save images")
    parser.add_argument("--graph-output", help="Save graph JSON")
    parser.add_argument("--output", help="Save report JSON")
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

    if args.graph_output:
        graph = build_identity_graph(signals)
        save_graph_json(args.graph_output, graph)
        print(f"[+] Graph saved to {args.graph_output}")

    if args.output:
        save_report(args.output, signals, temporal_data, stylometry_data)
        print(f"[+] Report saved to {args.output}")

    if args.images:
        plot_contributions_heatmap(signals, args.images)


if __name__ == "__main__":
    main()
