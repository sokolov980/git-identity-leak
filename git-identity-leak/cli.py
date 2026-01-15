# cli.py

import argparse
import os
import json

from analysis import full_analysis
from graph import build_identity_graph, save_graph_json
from report import save_report
from self_audit import self_audit

def main():
    parser = argparse.ArgumentParser(description="Git Identity Leak: OSINT tool for digital footprint analysis")
    parser.add_argument("--username", type=str, required=True, help="Target username to analyze")
    parser.add_argument("--check-username", action="store_true", help="Check username reuse across platforms")
    parser.add_argument("--check-email", action="store_true", help="Check email signals")
    parser.add_argument("--check-posts", action="store_true", help="Check posts/signals from platforms")
    parser.add_argument("--images", type=str, help="Directory to download/analyze images")
    parser.add_argument("--graph-output", type=str, help="Path to save identity graph JSON")
    parser.add_argument("--output", type=str, help="Path to save full report JSON")
    parser.add_argument("--temporal", action="store_true", help="Include temporal analysis")
    parser.add_argument("--stylometry", action="store_true", help="Include stylometry analysis")
    parser.add_argument("--self-audit", action="store_true", help="Perform self-audit on your own username")
    parser.add_argument("--verbose", action="store_true", help="Verbose debug output")
    
    args = parser.parse_args()

    if args.self_audit:
        if args.verbose:
            print(f"[DEBUG] Performing self-audit for {args.username}")
        self_audit(args.username)
        return

    if args.verbose:
        print(f"[DEBUG] Performing full analysis for {args.username}")

    signals, temporal_data, stylometry_data = full_analysis(
        username=args.username,
        image_dir=args.images,
        include_stylometry=args.stylometry,
        include_temporal=args.temporal
    )

    if args.verbose:
        print(f"[DEBUG] Signals collected: {len(signals)}")

    # Save JSON report
    if args.output:
        save_report(signals, temporal_data, stylometry_data, args.output)
        print(f"[+] Report saved to {args.output}")

    # Build identity graph
    if args.graph_output:
        graph = build_identity_graph(signals)
        save_graph_json(graph, args.graph_output)
        print(f"[+] Graph saved to {args.graph_output}")

    if args.verbose:
        print(f"[DEBUG] Temporal data: {temporal_data}")
        print(f"[DEBUG] Stylometry data: {stylometry_data}")

    # Summary
    overall_risk = "MEDIUM"  # Placeholder; could integrate risk.py
    print(f"[+] Overall risk: {overall_risk}")
    print("[+] Analysis complete.")

if __name__ == "__main__":
    main()
