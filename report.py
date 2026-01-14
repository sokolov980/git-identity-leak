import json

def print_report(username, findings, verbose=False):
    print(f"\n[ git-identity-leak report for '{username}' ]\n")

    if findings["author_names"]:
        print("[+] Author Name Signals:")
        for n in findings["author_names"]:
            print(f"    - {n['value']} (confidence: {n['confidence']})")
    else:
        print("[-] No author name signals detected.")

    if findings["emails"]:
        print("\n[+] Email Signals:")
        for e in findings["emails"]:
            print(f"    - {e['value']} (confidence: {e['confidence']})")
    else:
        print("\n[-] No email signals detected.")

    if findings["timezones"]:
        print("\n[+] Timezone Signals:")
        for tz in findings["timezones"]:
            print(f"    - {tz['value']} (confidence: {tz['confidence']})")
    else:
        print("\n[-] No timezone signals detected.")

    print(f"\n[!] Overall re-identification risk: {findings['overall_risk']}\n")

    if verbose:
        print("[DEBUG] Full findings data:")
        print(json.dumps(findings, indent=2))

def save_json(findings, filepath):
    with open(filepath, "w") as f:
        json.dump(findings, f, indent=2)
