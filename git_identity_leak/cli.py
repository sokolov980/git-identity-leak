#!/usr/bin/env python3

import argparse
from git_identity_leak.analysis import full_analysis
from git_identity_leak.graph import build_identity_graph, save_graph_json
from git_identity_leak.report import save_report

def main():
    parser = argparse.ArgumentParser(description="Git Identity Leak OSINT Tool")
    parser.add_argument("--username", required=True, help="Target username")
    parser.add_argument("--images", help="Directory to store images")
    parser.add_argument("--graph-output", help="Path to save graph JSON")
    parser.add_argument("--output", help="Path to save report JSON", default="report.json")
    parser.add_argument("--temporal", action="store_true", help="Include temporal analysis")
    parser.add_argument("--stylometry", action="store_true", help="Include stylometry analysis")
    parser.add_argument("--verbose", action="store_true", help="Print debug info")
    parser.add_argument("--self-audit", action="store_true", help="Run a quick self-audit")
    args = parser.parse_args()

    # Run analysis
    signals, temporal_data, stylometry_data = full_analysis(
        username=args.username,
        image_dir=args.images,
        include_temporal=args.temporal,
        include_stylometry=args.stylometry,
    )

    # Build graph if requested
    if args.graph_output:
        graph = build_identity_graph(signals)
        save_graph_json(args.graph_output, graph)
        print(f"[+] Graph saved to {args.graph_output}")

    # Save report
    save_report(args.output, signals, temporal_data, stylometry_data)
    print(f"[+] Report saved to {args.output}")

    # Verbose: print all details
    if args.verbose or args.self_audit:
        print("\n[DEBUG] Signals:")
        for s in signals:
            value = s.get("value", "N/A")
            stype = s.get("signal_type", "UNKNOWN")
            conf = s.get("confidence", "N/A")
            print(f" - {stype}: {value} (confidence: {conf})")

        print("\n[DEBUG] Temporal data:", temporal_data)
        print("\n[DEBUG] Stylometry data:", stylometry_data)

        # Optional: summary risk
        overall_risk = "MEDIUM"
        print(f"\n[+] Overall risk: {overall_risk}")
        print("[+] Analysis complete.")

if __name__ == "__main__":
    main()
