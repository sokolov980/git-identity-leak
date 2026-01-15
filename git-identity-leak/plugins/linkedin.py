# git_identity_leak/plugins/linkedin.py
import requests

def collect(username):
    """
    Check if a public LinkedIn profile exists for the username.
    Returns a signal dict.
    """
    signals = []
    linkedin_url = f"https://www.linkedin.com/in/{username}/"

    try:
        response = requests.head(linkedin_url, timeout=10, allow_redirects=True)
        if response.status_code == 200:
            signals.append({
                "signal_type": "PROFILE_LINKEDIN",
                "value": f"Public LinkedIn profile detected for {username}",
                "confidence": "MEDIUM"
            })
        else:
            signals.append({
                "signal_type": "PROFILE_LINKEDIN",
                "value": "No public LinkedIn profile detected",
                "confidence": "LOW"
            })

    except requests.exceptions.RequestException:
        signals.append({
            "signal_type": "PROFILE_LINKEDIN",
            "value": f"Unable to verify LinkedIn profile for {username}",
            "confidence": "LOW"
        })

    return signals
