# git_identity_leak/cli.py

import argparse
import json
import os
from datetime import datetime
import calendar

from git_identity_leak.analysis import full_analysis
from git_identity_leak.graph import build_identity_graph, save_graph_json
from git_identity_leak.report import save_report

# plotting
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

TRUNCATE_LEN = 120

def pretty_print_signals(signals, temporal_data=None, stylometry_data=None):
    print("\n[DEBUG] Signals:")
    if not signals:
        print("No signals collected.")
        return

    headers = ["TYPE", "VALUE", "CONFIDENCE"]
    widths = [30, 100, 10]
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
        value = s.get("value", "")
        conf = s.get("confidence", "")

        # Handle contributions specially
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
        elif stype in ("REPO_SUMMARY", "CONTRIBUTIONS_YEARLY_DATES"):
            # Don't truncate these
            print(f"{stype:<{widths[0]}} {str(value):<{widths[1]}} {conf:<{widths[2]}}")
            continue
        elif stype in ("GITHUB_PAGES", "PRONOUNS", "PROFILE_PLATFORM"):
            extra_info.append((stype, value, conf))
            continue

        # General truncation
        if len(str(value)) > TRUNCATE_LEN:
            value = str(value)[:TRUNCATE_LEN - 3] + "..."

        print(f"{stype:<{widths[0]}} {value:<{widths[1]}} {conf:<{widths[2]}}")

    # Contributions
    if contrib_total:
        print(f"{'CONTRIBUTION_TOTAL':<{widths[0]}} {contrib_total:<{widths[1]}} {'HIGH':<{widths[2]}}")
    if contrib_pattern:
        print(f"{'CONTRIBUTION_TIME_PATTERN':<{widths[0]}} {contrib_pattern:<{widths[1]}} {'MEDIUM':<{widths[2]}}")
    for year in sorted(contrib_years.keys()):
        value = f"{year}: {contrib_years[year]}"
        print(f"{'CONTRIBUTIONS_YEAR':<{widths[0]}} {value:<{widths[1]}} {'HIGH':<{widths[2]}}")
    for stype, value, conf in extra_info:
        print(f"{stype:<{widths[0]}} {value:<{widths[1]}} {conf:<{widths[2]}}")

    # Temporal data
    if temporal_data:
        print("\n[DEBUG] Temporal data:")
        print(json.dumps(temporal_data, indent=2))
    # Stylometry data
    if stylometry_data:
        print("\n[DEBUG] Stylometry data:")
        print(json.dumps(stylometry_data, indent=2))


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
        # Sunday=0, Monday=1, ..., Saturday=6
        weekday = (dt.weekday() + 1) % 7  # shift Monday=0 -> Sunday=0
        heatmap[weekday, week] = d["count"]

    plt.figure(figsize=(weeks / 2, 3))
    sns.heatmap(heatmap, cmap="Greens", cbar=True, linewidths=0.5, square=True)

    # Y-axis: show only Mon, Wed, Fri
    y_labels = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    plt.yticks([1, 3, 5], ["Mon", "Wed", "Fri"], rotation=0)
    plt.xticks([])

    # X-axis months
    month_positions = []
    month_labels = []
    for m in range(1, 13):
        try:
            month_date = datetime(start.year, m, 1)
            week_index = (month_date - start).days // 7
            if 0 <= week_index < weeks:
                month_positions.append(week_index)
                month_labels.append(calendar.month_abbr[m])
        except ValueError:
            continue
    plt.xticks(month_positions, month_labels, rotation=0, ha='center', fontsize=8, color="black", position=(0.0,1.02))

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

    # old-style flags
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
        include_stylometry=args.stylometry,
        check_username=args.check_username,
        check_email=args.check_email,
        check_posts=args.check_posts,
    )

    if args.verbose:
        pretty_print_signals(signals, temporal_data, stylometry_data)

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
