# git_identity_leak/cli.py
import argparse
import json
import os
from git_identity_leak.analysis import full_analysis
from git_identity_leak.graph import build_identity_graph, save_graph_json
from git_identity_leak.report import save_report

TRUNCATE_LEN = 120  # Increase so URLs are fully visible

def pretty_print_signals(signals, max_value_len=200):
    """
    Print collected signals in a neat table format.
    Dynamically adjusts VALUE column based on the longest signal.
    """
    print("[DEBUG] Signals:")
    if not signals:
        print("  No signals collected.")
        return

    # Determine the max width of VALUE column dynamically
    value_len = min(max(len(str(s.get("value", ""))) for s in signals), max_value_len)
    type_width = 18
    confidence_width = 10

    # Header
    print("-" * (type_width + value_len + confidence_width + 4))
    print(f"{'TYPE':<{type_width}} {'VALUE':<{value_len}} {'CONFIDENCE':<{confidence_width}}")
    print("-" * (type_width + value_len + confidence_width + 4))

    # Rows
    for s in signals:
        signal_type = s.get("signal_type", "UNKNOWN")
        value = str(s.get("value", ""))
        confidence = s.get("confidence", "")

        # Truncate only if extremely long
        display_value = value if len(value) <= value_len else value[:value_len-3] + "..."
        print(f"{signal_type:<{type_width}} {display_value:<{value_len}} {confidence:<{confidence_width}}")

    print("-" * (type_width + value_len + confidence_width + 4))

def pretty_print_dict(title, d):
    """
    Pretty-print a dictionary in JSON format.
    """
    print(f"[DEBUG] {title}:")
    if not d:
        print("  No data.")
        return
    print(json.dumps(d, indent=2))

def main():
    parser = argparse.ArgumentParser(description="Git Identity Leak OSINT Tool")
    parser.add_argument("--username", required=True, help="Target username to analyze")
    parser.add_argument("--self-audit", action="store_true", help="Run self-audit only")
    parser.add_argument("--images", help="Directory to store images")
    parser.add_argument("--graph-output", help="File to save graph JSON")
    parser.add_argument("--output", help="File to save report JSON")
    parser.add_argument("--temporal", action="store_true", help="Include temporal analysis")
    parser.add_argument("--stylometry", action="store_true", help="Include stylometry analysis")
    parser.add_argument("--verbose", action="store_true", help="Show debug output")
    args = parser.parse_args()

    # Ensure image directory exists
    if args.images:
        try:
            os.makedirs(args.images, exist_ok=True)
        except Exception as e:
            print(f"[!] Could not create image directory '{args.images}': {e}")
            args.images = None

    # Run full analysis
    signals, temporal_data, stylometry_data = full_analysis(
        username=args.username,
        image_dir=args.images,
        include_temporal=args.temporal,
        include_stylometry=args.stylometry
    )

    # Pretty-print debug output
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

if __name__ == "__main__":
    main()
