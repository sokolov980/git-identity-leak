def print_report(username, findings):
    print(f"\n[ git-identity-leak report for '{username}' ]\n")

    if findings["real_name_exposed"]:
        print("[+] Real name exposure detected:")
        for name in findings["real_name_exposed"]:
            print(f"    - {name}")
    else:
        print("[-] No obvious real-name leakage detected.")

    if findings["personal_emails"]:
        print("\n[+] Personal email addresses found in commits:")
        for email in findings["personal_emails"]:
            print(f"    - {email}")
    else:
        print("\n[-] No personal email domains detected.")

    if findings["timezone_inferred"]:
        print("\n[+] Timezone inference possible:")
        for tz in findings["timezone_inferred"]:
            print(f"    - {tz}")
    else:
        print("\n[-] No timezone inference possible.")

    print("\n[!] Interpretation:")
    print("    Independent public metadata signals can be correlated")
    print("    to reduce anonymity and increase identity confidence.\n")
