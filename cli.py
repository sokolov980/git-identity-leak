import argparse
from analysis import full_analysis
from graph import build_identity_graph, save_graph_json
from risk import compute_risk
from self_audit import self_audit

def main():
    parser = argparse.ArgumentParser(description="Git Identity Leak OSINT Tool")
    parser.add_argument("--username", type=str, help="Username to analyze", required=False)
    parser.add_argument("--check-username", action="store_true")
    parser.add_argument("--check-email", action="store_true")
    parser.add_argument("--check-posts", action="store_true")
    parser.add_argument("--images", type=str, help="Directory with images")
    parser.add_argument("--graph-output", type=str, help="Save identity graph JSON")
    parser.add_argument("--output", type=str, help="Save structured report JSON")
    parser.add_argument("--self-audit", action="store_true")
    parser.add_argument("--temporal", action="store_true")
    parser.add_argument("--stylometry", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    if args.self_audit and args.username:
        self_audit(args.username)
        return

    if not args.username:
        print("[!] Please provide a username for analysis or self-audit")
        return

    # Run full analysis
    signals, temporal_data, stylometry_data = full_analysis(
        username=args.username,
        image_dir=args.images,
        include_temporal=args.temporal,
        include_stylometry=args.stylometry
    )

    # Build confidence-weighted identity graph
    graph = build_identity_graph(signals)

    if args.graph_output:
        save_graph_json(graph, args.graph_output)
        if args.verbose:
            print(f"[+] Graph saved to {args.graph_output}")

    # Compute risk summary
    risk_summary = compute_risk(signals, graph)

    if args.output:
        import json
        report = {
            "signals": [s.__dict__ for s in signals],
            "temporal": temporal_data,
            "stylometry": stylometry_data,
            "risk_summary": risk_summary
        }
        with open(args.output, "w") as f:
            json.dump(report, f, indent=2)
        if args.verbose:
            print(f"[+] Report saved to {args.output}")

    # Verbose CLI output
    if args.verbose:
        print("\n[DEBUG] Signals:")
        for s in signals:
            print(f" - {s.type}:{s.value} ({s.signal_type}, conf={s.confidence})")
        print("\n[DEBUG] Temporal data:", temporal_data)
        print("\n[DEBUG] Stylometry data:", stylometry_data)
        print("\n[DEBUG] Risk summary:", risk_summary)

    print(f"\n[+] Overall risk: {risk_summary['overall_risk']}")
    print("[+] Analysis complete.")

if __name__ == "__main__":
    main()
