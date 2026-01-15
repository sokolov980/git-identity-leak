# cli.py

import argparse
import os
from analysis import full_analysis
from report import save_report
from graph import build_identity_graph, save_graph_json
from self_audit import self_audit

def main():
    parser = argparse.ArgumentParser(description="Git Identity Leak CLI")
    parser.add_argument("--username", type=str, required=True)
    parser.add_argument("--check-username", action="store_true")
    parser.add_argument("--check-email", action="store_true")
    parser.add_argument("--check-posts", action="store_true")
    parser.add_argument("--images", type=str)
    parser.add_argument("--graph-output", type=str)
    parser.add_argument("--output", type=str)
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

    if args.output:
        save_report(signals, temporal_data, stylometry_data, args.output)

    if args.graph_output:
        graph = build_identity_graph(signals)
        save_graph_json(graph, args.graph_output)

    print("[+] Analysis complete.")

if __name__ == "__main__":
    main()
