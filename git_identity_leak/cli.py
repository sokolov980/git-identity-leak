# git_identity_leak/cli.py
import argparse
import json
import os
from datetime import datetime
from git_identity_leak.analysis import full_analysis
from git_identity_leak.graph import build_identity_graph, save_graph_json, nx
from git_identity_leak.report import save_report

# Optional plotting
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    HAS_PLOTTING = True
except ImportError:
    HAS_PLOTTING = False

TRUNCATE_LEN = 120  # for console output

def pretty_print_signals(signals, truncate_len=TRUNCATE_LEN):
    """
    Pretty print signals like before.
    """
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
    extra_info = []

    for s in signals:
        stype = s.get("signal_type", "UNKNOWN")
        value = str(s.get("value", ""))
        confidence = s.get("confidence", "")

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
            extra_info.append((stype, value, confidence))
            continue

        if stype == "REPO_SUMMARY":
            parts = [p.strip() for p in value.split("|")]
            print(f"{stype:<{col_widths[0]}} {parts[0]:<{col_widths[1]}} {confidence:<{col_widths[2]}}")
            for part in parts[1:]:
                print(f"{'':<{col_widths[0]}} {part:<{col_widths[1]}}")
            continue

        display_value = value if len(value) <= truncate_len else value[:truncate_len - 3] + "..."
        print(f"{stype:<{col_widths[0]}} {display_value:<{col_widths[1]}} {confidence:<{col_widths[2]}}")

    # Print contributions last
    if contrib_total is not None:
        print(f"{'CONTRIBUTION_TOTAL':<{col_widths[0]}} {contrib_total:<{col_widths[1]}} HIGH")
    if contrib_pattern is not None:
        print(f"{'CONTRIBUTION_TIME_PATTERN':<{col_widths[0]}} {contrib_pattern:<{col_widths[1]}} MEDIUM")
    for year in sorted(contrib_years.keys()):
        print(f"{'CONTRIBUTIONS_YEAR':<{col_widths[0]}} {year}: {contrib_years[year]:<{col_widths[1]}} HIGH")
    for stype, value, confidence in extra_info:
        display_value = value if len(value) <= truncate_len else value[:truncate_len - 3] + "..."
        print(f"{stype:<{col_widths[0]}} {display_value:<{col_widths[1]}} {confidence:<{col_widths[2]}}")

    print(divider)

def plot_contributions_heatmap(signals, image_dir):
    """
    Plots a GitHub-style weekly heatmap using daily contributions.
    """
    if not HAS_PLOTTING:
        print("[!] matplotlib/seaborn not installed, cannot plot contributions heatmap.")
        return

    daily_signal = next((s for s in signals if s["signal_type"] == "CONTRIBUTIONS_YEARLY_DATES"), None)
    if not daily_signal:
        print("[!] No daily contributions data found.")
        return

    # Build a 7x52 grid (week x weekday)
    import numpy as np
    from matplotlib.colors import ListedColormap

    days = daily_signal["value"]  # list of {"date": "YYYY-MM-DD", "count": N}
    contributions = np.zeros((7, 53), dtype=int)  # Mon-Sun rows, week columns

    start_date = datetime.strptime(days[0]["date"], "%Y-%m-%d")
    for d in days:
        dt = datetime.strptime(d["date"], "%Y-%m-%d")
        week = (dt - start_date).days // 7
        weekday = dt.weekday()  # 0=Mon
        if week >= 53:  # safety for leap years
            continue
        contributions[weekday, week] = d["count"]

    plt.figure(figsize=(12, 4))
    sns.heatmap(contributions, cmap="Greens", cbar=True, linewidths=0.5, linecolor="gray")
    plt.title(f"GitHub Contributions Heatmap ({daily_signal['source']})")
    plt.ylabel("Weekday (Mon-Sun)")
    plt.xlabel("Week Number")
    plt.tight_layout()

    if image_dir:
        os.makedirs(image_dir, exist_ok=True)
        path = os.path.join(image_dir, f"{daily_signal['source']}_contributions.png")
        plt.savefig(path)
        print(f"[+] Contributions heatmap saved to {path}")
    else:
        plt.show()

def pretty_print_dict(title, d):
    print(f"[DEBUG] {title}:")
    if not d:
        print("  No data.")
        return
    print(json.dumps(d, indent=2))

def main():
    parser = argparse.ArgumentParser(description="Git Identity Leak OSINT Tool")
    parser.add_argument("--username", required=True, help="Target username to analyze")
    parser.add_argument("--self-audit", action="store_true", help="Run self-audit only")
    parser.add_argument("--images", help="Directory to save images (heatmaps)")
    parser.add_argument("--graph-output", help="File to save graph JSON")
    parser.add_argument("--output", help="File to save report JSON")
    parser.add_argument("--temporal", action="store_true", help="Include temporal analysis")
    parser.add_argument("--stylometry", action="store_true", help="Include stylometry analysis")
    parser.add_argument("--verbose", action="store_true", help="Show debug output")
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

    # Build and save graph
    graph = build_identity_graph(signals)
    if args.graph_output:
        save_graph_json(args.graph_output, graph)
        print(f"[+] Graph saved to {args.graph_output}")

    # Save report
    if args.output:
        save_report(args.output, signals, temporal_data, stylometry_data)
        print(f"[+] Report saved to {args.output}")

    # Plot contributions heatmap
    if args.images:
        plot_contributions_heatmap(signals, args.images)

if __name__ == "__main__":
    main()
