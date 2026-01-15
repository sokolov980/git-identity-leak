# git-identity-leak/cli.py

import argparse
import os
import json
from analysis import full_analysis
from graph import build_identity_graph, save_graph_json
from report import save_report
from self_audit import self_audit

# Optional: add color for warnings (works in most terminals)
class Colors:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RESET = "\033[0m"

def pretty_print_signals(signals):
    print("\n[DEBUG] Signals:")
    if not signals:
        print(" - No signals found.")
        return
    for s in signals:
        signal_type = s.get("signal_type", "unknown")
        value = s.get("value", "N/A")
        confidence = s.get("confidence", "N/A")
        print(f" - {signal_type}: {value} (confidence={confidence})")

def pretty_print_temporal(temporal_data):
    print("\n[DEBUG] Temporal data:")
    if not temporal_data:
        print(" - No temporal data available.")
        return
    for k, v in temporal_data.items():
        print(f" - {k}: {v}")

def pretty_print_stylometry(stylometry_data):
    print("\n[DEBUG] Stylometry data:")
    if not stylometry_data:
        print(" - No stylometry data available.")
        return
    for k, v in stylometry_data.items():
        print(f" - {k}: {v}")

def main():
    parser = argparse.ArgumentParser(description="Git Identity Leak - OSINT tool")
    parser.add_argument("--username", required=True)
    parser.add_argument("--check-username", action="store_true")
    parser.add_argument("--check-email", action="store_true")
    parser.add_argument("--check-posts", action="store_true")
    parser.add_argument("--images", type=str, help="Directory to store images")
    parser.add_argument("--graph-output", type=str, help="Path to save graph JSON")
    parser.add_argument("--output", type=str, help="Path to save report JSON")
    parser.add_argument("--temporal", action="store_true")
    parser.add_argument("--stylometry", action="store_true")
    parser.add_argument("--self-audit", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    if args.self_audit:
        self_audit(args.username)
        return

    signals, temporal_data, stylometry_data = full_analysis(
        username=args.username,
        image_dir=args.images,
        include_stylometry=args.stylometry,
        include_temporal=args.temporal
    )

    # Save graph
    if args.graph_output:
        graph = build_identity_graph(signals)
        save_graph_json(graph, args.graph_output)
        print(f"{Colors.GREEN}[+] Graph saved to {args.graph_output}{Colors.RESET}")

    # Save report
    if args.output:
        save_report(signals, temporal_data, stylometry_data, args.output)
        print(f"{Colors.GREEN}[+] Report successfully saved to {args.output}{Colors.RESET}")

    # Verbose / debug output
    if args.verbose:
        pretty_print_signals(signals)
        pretty_print_temporal(temporal_data)
        pretty_print_stylometry(stylometry_data)

if __name__ == "__main__":
    main()
