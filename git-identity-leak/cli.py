# git_identity_leak/cli.py
import argparse
import os
import json
from analysis import full_analysis
from graph import build_identity_graph, save_graph_json
from report import save_report
from self_audit import self_audit

def main():
    parser = argparse.ArgumentParser(description="Git Identity Leak: OSINT self-audit and analysis")
    parser.add_argument("--username", required=True, help="Target username to analyze")
    parser.add_argument("--images", help="Directory to store images", default="images")
    parser.add_argument("--graph-output", help="Path to save graph JSON", default="graph.json")
    parser.add_argument("--output", help="Path to save full report JSON", default="report.json")
    parser.add_argument("--check-username", action="store_true", help="Check username reuse")
    parser.add_argument("--check-email", action="store_true", help="Check email reuse")
    parser.add_argument("--check-posts", action="store_true", help="Check posts on social platforms")
    parser.add_argument("--self-audit", action="store_true", help="Run a quick self-audit")
    parser.add_argument("--temporal", action="store_true", help="Include temporal analysis")
    parser.add_argument("--stylometry", action="store_true", help="Include stylometry analysis")
    parser.add_argument("--verbose", action="store_true", help="Verbose output for debugging")
    args = parser.parse_args()

    username = args.username
    image_dir = args.images

    if args.self_audit:
        print(f"Running self-audit for {username}...")
        self_audit(username)
        return

    # Ensure image directory exists
    if image_dir:
        os.makedirs(image_dir, exist_ok=True)

    print(f"Performing full analysis for {username}...")
    signals, temporal_data, stylometry_data = full_analysis(
        username,
        image_dir=image_dir,
        include_stylometry=args.stylometry,
        include_temporal=args.temporal
    )

    if args.verbose:
        print("\n[DEBUG] Signals:", signals)
        print("\n[DEBUG] Temporal data:", temporal_data)
        print("\n[DEBUG] Stylometry data:", stylometry_data)

    # Build graph
    graph = build_identity_graph(signals)
    save_graph_json(graph, args.graph_output)
    print(f"[+] Graph saved to {args.graph_output}")

    # Save report
    report_data = {
        "signals": signals,
        "temporal_data": temporal_data,
        "stylometry_data": stylometry_data
    }
    save_report(report_data, args.output)
    print(f"[+] Report saved to {args.output}")

    print("\n[+] Analysis complete.")

if __name__ == "__main__":
    main()
