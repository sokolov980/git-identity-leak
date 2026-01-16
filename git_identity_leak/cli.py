#!/usr/bin/env python3
import argparse
from analysis import full_analysis
from graph import build_identity_graph, save_graph_json
from report import save_report
from self_audit import self_audit

def main():
    parser = argparse.ArgumentParser(description="Git Identity Leak Analyzer")
    parser.add_argument("--username", required=True, help="Target username")
    parser.add_argument("--self-audit", action="store_true", help="Run self-audit only")
    parser.add_argument("--images", help="Directory to save images")
    parser.add_argument("--graph-output", help="Path to save graph JSON")
    parser.add_argument("--output", help="Path to save report JSON")
    parser.add_argument("--temporal", action="store_true", help="Include temporal analysis")
    parser.add_argument("--stylometry", action="store_true", help="Include stylometry analysis")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()

    if args.self_audit:
        self_audit(args.username)
        return

    signals, temporal_data, stylometry_data = full_analysis(
        username=args.username,
        image_dir=args.images,
        include_temporal=args.temporal,
        include_stylometry=args.stylometry
    )

    if args.graph_output:
        graph = build_identity_graph(signals)
        save_graph_json(graph, args.graph_output)

    if args.output:
        save_report(args.output, signals, temporal_data, stylometry_data)

    if args.verbose:
        print(f"[DEBUG] Signals: {signals}")
        print(f"[DEBUG] Temporal data: {temporal_data}")
        print(f"[DEBUG] Stylometry data: {stylometry_data}")

    print("[+] Analysis complete.")

if __name__ == "__main__":
    main()
