import json

def print_report(username, findings, verbose=False):
    print(f"\n[ git-identity-leak report for '{username}' ]\n")

    # Author names
    for key in ["author_names", "emails", "timezones", "images", "username_reuse", "email_reuse"]:
        signals = findings.get(key)
        if signals:
            print(f"[+] {key.replace('_',' ').title()}:")
            for s in signals:
                display = s.get("value") if "value" in s else (s.get("site") + " → " + str(s.get("found")))
                confidence = s.get("confidence", "LOW")
                print(f"    - {display} (confidence: {confidence})")
        else:
            print(f"[-] {key.replace('_',' ').title()} not detected.")

    overall = findings.get("overall_risk", "MEDIUM")
    print(f"\n[!] Overall re-identification risk: {overall}\n")

    if verbose:
        print("[DEBUG] Full findings data:")
        print(json.dumps(findings, indent=2))

def save_json(findings, filepath):
    with open(filepath, "w") as f:
        json.dump(findings, f, indent=2)
