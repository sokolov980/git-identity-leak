import sys
from github import fetch_commit_metadata
from analysis import analyze_leaks
from report import print_report

def main():
    if len(sys.argv) != 3 or sys.argv[1] != "analyze":
        print("Usage: python main.py analyze <github_username>")
        sys.exit(1)

    username = sys.argv[2]

    commits = fetch_commit_metadata(username)
    if not commits:
        print("No public commit data found.")
        sys.exit(0)

    findings = analyze_leaks(username, commits)
    print_report(username, findings)

if __name__ == "__main__":
    main()
