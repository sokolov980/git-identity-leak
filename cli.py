import argparse
from github_api import fetch_commit_metadata
from analysis import analyze_commits
from report import print_report, save_json
from images import analyze_images
from reuse import check_username, check_email

def main():
    parser = argparse.ArgumentParser(description="GitHub + OSINT signal analyzer")
    parser.add_argument("--username", required=True, help="GitHub username to analyze")
    parser.add_argument("--max-commits", type=int, default=50, help="Max commits per repo")
    parser.add_argument("--images", help="Folder with images to analyze")
    parser.add_argument("--check-username", action="store_true", help="Check username reuse on public sites")
    parser.add_argument("--check-email", action="store_true", help="Check email reuse on public sites")
    parser.add_argument("--output", help="Optional JSON output file")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()

    commits = fetch_commit_metadata(args.username, max_commits=args.max_commits)
    findings = analyze_commits(args.username, commits) if commits else {}

    if args.images:
        findings["images"] = analyze_images(args.images)

    if args.check_username:
        findings["username_reuse"] = check_username(args.username)

    if args.check_email and commits:
        # pick first email for testing
        email = None
        for c in commits:
            if c.get("author_email"):
                email = c["author_email"]
                break
        findings["email_reuse"] = check_email(email)

    print_report(args.username, findings, verbose=args.verbose)

    if args.output:
        save_json(findings, args.output)

if __name__ == "__main__":
    main()
