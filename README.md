# git-identity-leak

A CLI tool that demonstrates how public GitHub metadata can unintentionally reveal real-world identity.

---

## What This Is

`git-identity-leak` is a minimal OSINT experiment focused on **GitHub only**.

Given a GitHub username, it analyzes **public commit metadata** to highlight common
identity leaks such as:

- Real names in commit authorship
- Personal email addresses
- Timezone and activity pattern exposure
- Username reuse signals

This tool is designed to be run **on yourself** to understand how much identity
information you may be leaking unintentionally.

---

## What This Is NOT

- Not a people search tool
- Not a doxxing framework
- Not an enrichment or lookup service
- Not exhaustive

This is a **proof-of-viability experiment**.

---

## Usage

```bash
python main.py analyze <github_username>
```

Example:

```bash
python main.py analyze johndoe
```

---

## Output

The tool prints a short, human-readable report describing:

- What data was found

- Why it matters

- How it contributes to identity linkage risk

No data is stored.

---

## Ethics

- Public data only

- Passive analysis only

- No scraping behind authentication

- Intended for self-assessment and security research

---
