import argparse
from github_api import fetch_commit_metadata
from analysis import analyze_commits
from report import print_report, save_json

def main():
    parser = argparse.ArgumentParser(description="GitHub identity leakage analyzer")
    parser.add_argument("--username", required=True, help="GitHub username to analyze")
    parser.add_argument("--max-commits", type=int, default=50, help="Max commits per repo")
    parser.add_argument("--output", help="Optional JSON output file")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()

    commits = fetch_commit_metadata(args.username, max_commits=args.max_commits)
    if not commits:
        print("No public commit data found.")
        return

    findings = analyze_commits(args.username, commits)
    print_report(args.username, findings, verbose=args.verbose)

    if args.output:
        save_json(findings, args.output)

if __name__ == "__main__":
    main()
