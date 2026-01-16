import argparse
from git_identity_leak.analysis import full_analysis
from git_identity_leak.graph import build_identity_graph
from git_identity_leak.report import save_report
from git_identity_leak.self_audit import self_audit


def main():
    parser = argparse.ArgumentParser(description="Git Identity Leak")
    parser.add_argument("--username", required=True)
    parser.add_argument("--self-audit", action="store_true")
    parser.add_argument("--images")
    parser.add_argument("--graph-output")
    parser.add_argument("--output")
    parser.add_argument("--temporal", action="store_true")
    parser.add_argument("--stylometry", action="store_true")
    parser.add_argument("--verbose", action="store_true")

    args = parser.parse_args()

    if args.self_audit:
        self_audit(args.username)
        return

    signals, temporal_data, stylometry_data = full_analysis(
        username=args.username,
        image_dir=args.images,
        include_temporal=args.temporal,
        include_stylometry=args.stylometry,
    )

    if args.graph_output:
        graph = build_identity_graph(signals)
        with open(args.graph_output, "w") as f:
            f.write(graph)
        print(f"[+] Graph saved to {args.graph_output}")

    if args.output:
        save_report(
            args.output,
            signals,
            temporal_data,
            stylometry_data
        )

    if args.verbose:
        print("\n[DEBUG] Signals:")
        for s in signals:
            print(f" - {s['signal_type']}: {s['value']} ({s['confidence']})")

        print("\n[DEBUG] Temporal data:", temporal_data)
        print("[DEBUG] Stylometry data:", stylometry_data)

    print("[+] Analysis complete.")


if __name__ == "__main__":
    main()
