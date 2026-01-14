import re
from collections import Counter

FREE_EMAIL_DOMAINS = {
    "gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "proton.me", "protonmail.com"
}

def analyze_leaks(username, commits):
    names = []
    emails = []
    timezones = []

    for c in commits:
        if c["author_name"]:
            names.append(c["author_name"])

        if c["author_email"]:
            emails.append(c["author_email"])

        if c["timestamp"] and c["timestamp"].endswith("Z"):
            timezones.append("UTC")

    findings = {}

    name_counts = Counter(names)
    email_counts = Counter(emails)

    findings["real_name_exposed"] = [
        name for name, count in name_counts.items()
        if name.lower() != username.lower() and count > 1
    ]

    findings["personal_emails"] = [
        email for email in email_counts
        if email.split("@")[-1] in FREE_EMAIL_DOMAINS
    ]

    findings["unique_emails"] = list(email_counts.keys())
    findings["timezone_inferred"] = list(set(timezones))

    return findings
