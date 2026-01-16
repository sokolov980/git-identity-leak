# git_identity_leak/cli.py
import argparse
import json
import os
from git_identity_leak.analysis import full_analysis
from git_identity_leak.graph import build_identity_graph, save_graph_json
from git_identity_leak.report import save_report

TRUNCATE_LEN = 60

def pretty_print_signals(signals, truncate_len=TRUNCATE_LEN):
    """
    Print collected signals in a neat table format, truncating long values.
    """
    print("[DEBUG] Signals:")
    if not signals:
        print("  No signals collected.")
        return

    headers = ["TYPE", "VALUE", "CONFIDENCE"]
    print("-" * (truncate_len + 30))
    print(f"{headers[0]:<15} {headers[1]:<{truncate_len}} {headers[2]:<10}")
    print("-" * (truncate_len + 30))

    for s in signals:
        signal_type = s.get("signal_type", "UNKNOWN")
        value = str(s.get("value", ""))
        confidence = s.get("confidence", "")

        if len(value) > truncate_len:
            value = value[:truncate_len - 3] + "..."

        print(f"{signal_type:<15} {value:<{truncate_len}} {confidence:<10}")

    print("-" * (truncate_len + 30))

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
