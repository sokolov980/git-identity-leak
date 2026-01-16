import argparse
from git_identity_leak.analysis import full_analysis
from git_identity_leak.graph import build_identity_graph
from git_identity_leak.report import save_report
from git_identity_leak.self_audit import self_audit


def main():
    parser = argparse.ArgumentParser(description="Git Identity Leak Detector")

    parser.add_argument("--username", required=True)
    parser.add_argument("--images")
    parser.add_argument("--graph-output")
    parser.add_argument("--output")
    parser.add_argument("--temporal", action="store_true")
    parser.add_argument("--stylometry", action="store_true")
    parser.add_argument("--self-audit", action="store_true")
    parser.add_argument("--verbose", action="store_true")

    args = parser.parse_args()

    if args.self_audit:
        self_audit(args.username)
        return

    signals, temporal, stylometry = full_analysis(
        args.username,
        image_dir=args.images,
        include_temporal=args.temporal,
        include_stylometry=args.stylometry,
    )

    if args.graph_output:
        graph = build_identity_graph(signals)
        with open(args.graph_output, "w") as f:
            import json
            json.dump(graph, f, indent=2)
        print(f"[+] Graph saved to {args.graph_output}")

    report = {
        "username": args.username,
        "signals": signals,
        "temporal": temporal,
        "stylometry": stylometry,
    }

    if args.output:
        save_report(report, args.output)

    if args.verbose:
        print("[DEBUG] Signals:", signals)
        print("[DEBUG] Temporal data:", temporal)
        print("[DEBUG] Stylometry data:", stylometry)

    print("[+] Analysis complete.")


if __name__ == "__main__":
    main()
