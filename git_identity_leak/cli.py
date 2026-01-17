import argparse
import json
import os
from datetime import datetime
from git_identity_leak.analysis import full_analysis
from git_identity_leak.graph import build_identity_graph, save_graph_json
from git_identity_leak.report import save_report

# --- Matplotlib for heatmap ---
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from matplotlib.colors import ListedColormap
from datetime import date, timedelta

TRUNCATE_LEN = 120  # URL display length

# --- Pretty print signals (unchanged) ---
def pretty_print_signals(signals, truncate_len=120):
    # same as your updated version
    ...

def pretty_print_dict(title, d):
    # same as before
    ...

# --- Contribution calendar heatmap ---
def plot_weekly_contribution_calendar(contributions, username, save_path=None):
    """
    contributions: list of dicts with 'date' (YYYY-MM-DD) and 'count' keys
    """
    if not contributions:
        print("[!] No contribution data available for calendar heatmap.")
        return

    # Prepare 52-week x 7-day array
    today = date.today()
    start_date = today - timedelta(weeks=52)
    # Map dates to 7x52 grid (columns: weeks, rows: Mon-Sun)
    grid = np.zeros((7, 53), dtype=int)

    for item in contributions:
        try:
            dt = datetime.strptime(item["date"], "%Y-%m-%d").date()
            if dt < start_date:
                continue
            week_idx = (dt - start_date).days // 7
            weekday = dt.weekday()  # Monday=0
            grid[weekday, week_idx] = item["count"]
        except Exception:
            continue

    # Plot heatmap
    plt.figure(figsize=(15,3))
    cmap = ListedColormap(['#ebedf0','#c6e48b','#7bc96f','#239a3b','#196127'])
    plt.imshow(grid, aspect='auto', cmap=cmap, interpolation='nearest')
    plt.title(f"GitHub-style Contribution Calendar: {username}")
    plt.yticks(range(7), ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'])
    plt.xticks([])
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path)
        print(f"[+] Weekly contribution calendar saved to {save_path}")
    else:
        plt.show()

# --- Main ---
def main():
    parser = argparse.ArgumentParser(description="Git Identity Leak OSINT Tool")
    parser.add_argument("--username", required=True, help="Target username to analyze")
    parser.add_argument("--images", help="Directory to save images (heatmap)")
    parser.add_argument("--graph-output", help="File to save graph JSON")
    parser.add_argument("--output", help="File to save report JSON")
    parser.add_argument("--verbose", action="store_true", help="Show debug output")
    args = parser.parse_args()

    if args.images:
        os.makedirs(args.images, exist_ok=True)

    # Run full analysis
    signals, temporal_data, stylometry_data = full_analysis(
        username=args.username,
        image_dir=args.images,
        include_temporal=True,
        include_stylometry=False
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

    # --- Prepare weekly contribution calendar ---
    contrib_signal = next((s for s in signals if s["signal_type"]=="CONTRIBUTIONS_YEARLY_DATES"), None)
    if contrib_signal:
        contributions = contrib_signal.get("value", [])  # list of {"date":..., "count":...}
        heatmap_path = os.path.join(args.images, f"{args.username}_weekly_calendar.png") if args.images else None
        plot_weekly_contribution_calendar(contributions, args.username, save_path=heatmap_path)

if __name__ == "__main__":
    main()
