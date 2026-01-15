from datetime import datetime

# Dummy platform lookup
PLATFORMS = ["GitHub", "GitLab", "Bitbucket", "Reddit", "Twitter", "LinkedIn"]

def check_username_reuse(username: str):
    results = []
    for platform in PLATFORMS:
        # Simulated check
        found = username.lower() in ["example", "test"]  # placeholder
        results.append({
            "site": platform,
            "found": found,
            "confidence": 0.8 if found else 0.3,
            "evidence": f"Profile check on {platform}",
            "first_seen": datetime.utcnow().isoformat(),
            "last_seen": datetime.utcnow().isoformat()
        })
    return results

def check_email_reuse(username: str):
    # Simulated email signal
    email = f"{username}@users.noreply.github.com"
    return [{
        "site": "GitHub",
        "value": email,
        "found": True,
        "confidence": 0.7,
        "evidence": "Public commit email",
        "first_seen": datetime.utcnow().isoformat(),
        "last_seen": datetime.utcnow().isoformat()
    }]
