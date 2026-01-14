from collections import Counter

FREE_EMAIL_DOMAINS = {"gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "proton.me"}

def analyze_commits(username, commits):
    names, emails, timezones = [], [], []

    for c in commits:
        if c.get("author_name"):
            names.append(c["author_name"])
        if c.get("author_email"):
            emails.append(c["author_email"])
        if c.get("timestamp") and c["timestamp"].endswith("Z"):
            timezones.append("UTC")

    findings = {}

    # Author name scoring
    name_counts = Counter(names)
    exposed_names = [n for n in name_counts if n.lower() != username.lower()]
    findings["author_names"] = [
        {"value": n, "confidence": "HIGH" if name_counts[n] > 1 else "LOW"}
        for n in exposed_names
    ]

    # Email scoring
    email_counts = Counter(emails)
    findings["emails"] = []
    for e in email_counts:
        domain = e.split("@")[-1]
        confidence = "LOW"
        if domain not in FREE_EMAIL_DOMAINS:
            confidence = "MEDIUM"
        findings["emails"].append({"value": e, "confidence": confidence})

    # Timezone scoring
    unique_tz = list(set(timezones))
    findings["timezones"] = [{"value": tz, "confidence": "MEDIUM"} for tz in unique_tz]

    # Overall risk
    findings["overall_risk"] = "HIGH" if findings["author_names"] or findings["emails"] else "LOW"
    return findings
