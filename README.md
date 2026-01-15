# git-identity-leak

**Git-Identity-Leak** is a command-line OSINT tool for mapping your digital footprint. It identifies public signals tied to a username, including profile names, emails, images, posts, and social media presence, and correlates them into a structured graph for analysis.  

> ⚠️ Use only on accounts you own or have permission to test. Unauthorized scraping of private accounts is illegal.  

---

## Features

- Collects public identity signals from multiple platforms:
  - GitHub: profile info, email, avatar, repo images
  - Reddit: public posts and comments
  - X (formerly Twitter): public posts via Nitter
  - LinkedIn: profile existence detection
- Detects username and email reuse across platforms
- Downloads and analyzes images from profile and repositories
- Generates structured JSON reports
- Builds a graph of correlated signals for visualization
- Optional temporal and stylometry analysis
- Fully CLI-driven with verbose logging

---

## Installation

**1.** Clone the repository:

```bash
git clone https://github.com/<your-username>/git-identity-leak.git
cd git-identity-leak/git-identity-leak
```

**2.** Create a virtual environment:
   
```bash
python3 -m venv venv
source venv/bin/activate
```

**3.** Install dependencies:
   
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Usage

### Basic self-audit

```bash
python3 cli.py --username <your-username> --self-audit
```

**Full OSINT analysis with images, reuse, graph, and report**

```bash
python3 cli.py \
  --username <username> \
  --check-username --check-email --check-posts \
  --images ./images \
  --graph-output graph.json \
  --output report.json \
  --temporal --stylometry \
  --verbose
```

---

## Output

- `report.json` — structured JSON report of all findings
- `graph.json` — graph data showing relationships between usernames, emails, and images
- `./images/` — downloaded images from GitHub avatars or repo READMEs

---

## Plugins

Plugins allow the tool to pull data from various public sources:

| Plugin    | Functionality                                |
|-----------|---------------------------------------------|
| GitHub    | Profile info, avatar, email, repo images    |
| Reddit    | Public posts/comments                        |
| X         | Public posts via Nitter                       |
| LinkedIn  | Detect public profile existence              |

> Missing plugins will show a friendly warning, e.g., `[!] Plugin X (formerly Twitter) not found. Skipping.`  

---

## Contributing

Contributions are welcome:

- Add new platform plugins (e.g., StackOverflow, Discord)
- Improve image analysis or stylometry detection
- Add additional graph visualization features

---

## License

MIT License — free to use for personal security research.

---

## Disclaimer

This tool is **intended for security research and self-auditing only**. Scanning or scraping accounts you do not own may violate laws and platform terms of service.

---
