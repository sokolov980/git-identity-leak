# git-identity-leak/cli.py

import argparse
import os

from analysis import full_analysis
from graph import build_identity_graph, save_graph_json
from report import save_report
from self_audit import self_audit

def main():
    parser = argparse.ArgumentParser(description="Git Identity Leak - OSINT Tool")
    parser.add_argument("--username", required=True, help="Username to analyze")
    parser.add_argument("--images", help="Directory to store images")
    parser.add_argument("--graph-output", help="Path to save graph JSON")
    parser.add_argument("--output", help="Path to save full report JSON")
    parser.add_argument("--check-username", action="store_true")
    parser.add_argument("--check-email", action="store_true")
    parser.add_argument("--check-posts", action="store_true")
    parser.add_argument("--self-audit", action="store_true")
    parser.add_argument("--temporal", action="store_true")
    parser.add_argument("--stylometry", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    if args.self_audit:
        self_audit(args.username)
        return

    # Full analysis
    signals, temporal_data, stylometry_data = full_analysis(
        username=args.username,
        image_dir=args.images,
        include_temporal=args.temporal,
        include_stylometry=args.stylometry
    )

    # Build graph
    graph = build_identity_graph(signals)
    if args.graph_output:
        save_graph_json(graph, args.graph_output)
        print(f"[+] Graph saved to {args.graph_output}")

    # Save report
    if args.output:
        save_report(signals, temporal_data, stylometry_data, args.output)
        print(f"[+] Report saved to {args.output}")

    if args.verbose:
        print("[DEBUG] Signals:", signals)
        print("[DEBUG] Temporal data:", temporal_data)
        print("[DEBUG] Stylometry data:", stylometry_data)

if __name__ == "__main__":
    main()
