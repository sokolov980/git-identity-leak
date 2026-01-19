# git_identity_leak/graph.py
import os
import json
import networkx as nx
from networkx.readwrite import json_graph


def build_identity_graph(signals):
    G = nx.Graph()
    username = next((s["value"] for s in signals if s["signal_type"] == "USERNAME"), None)

    # -------------------------
    # Base profile nodes
    # -------------------------
    for s in signals:
        stype, value = s.get("signal_type"), s.get("value")
        if not stype or value is None:
            continue

        node_id = f"{stype}:{value}"
        G.add_node(node_id, **s)

        if (
            username
            and stype
            not in (
                "REPO_SUMMARY",
                "INACTIVITY_SCORE",
                "CONTRIBUTIONS_YEAR",
                "CONTRIBUTION_TOTAL",
                "CONTRIBUTION_TIME_PATTERN",
                "CONTRIBUTION_HOURLY_PATTERN",
                "FOLLOWER_USERNAME",
                "FOLLOWING_USERNAME",
                "MUTUAL_CONNECTION",
            )
        ):
            G.add_edge(
                f"USERNAME:{username}",
                node_id,
                relation="PROFILE_INFO",
            )

    # -------------------------
    # Followers / Following
    # -------------------------
    if username:
        for s in signals:
            if s["signal_type"] in (
                "FOLLOWER_USERNAME",
                "FOLLOWING_USERNAME",
                "MUTUAL_CONNECTION",
            ):
                G.add_edge(
                    f"USERNAME:{username}",
                    f"{s['signal_type']}:{s['value']}",
                    relation="SOCIAL_LINK",
                )

    # -------------------------
    # Repo nodes
    # -------------------------
    repo_sigs = [s for s in signals if s.get("signal_type") == "REPO_SUMMARY"]
    inactivity_sigs = {
        s["value"].split(":")[0]: s
        for s in signals
        if s.get("signal_type") == "INACTIVITY_SCORE"
    }

    for repo in repo_sigs:
        repo_name = repo["value"].split("|")[0].strip()
        node_id = f"REPO:{repo_name}"
        node_data = repo.copy()

        if repo_name in inactivity_sigs:
            node_data["inactivity_score"] = inactivity_sigs[repo_name]["value"]

        G.add_node(node_id, **node_data)

        if username:
            G.add_edge(
                f"USERNAME:{username}",
                node_id,
                relation="OWNS_REPO",
            )

    # -------------------------
    # Contribution years (temporal)
    # -------------------------
    contrib_years = [
        s for s in signals if s.get("signal_type") == "CONTRIBUTIONS_YEAR" and "meta" in s
    ]
    contrib_years.sort(key=lambda s: int(s["meta"]["year"]))

    prev_node = None
    for s in contrib_years:
        year = s["meta"]["year"]
        node_id = f"CONTRIBUTIONS_YEAR:{year}"
        G.add_node(node_id, **s)

        if prev_node:
            G.add_edge(prev_node, node_id, relation="TEMPORAL_NEXT")

        prev_node = node_id

    # -------------------------
    # Total contributions
    # -------------------------
    total_signal = next(
        (s for s in signals if s["signal_type"] == "CONTRIBUTION_TOTAL"), None
    )

    if total_signal:
        G.add_node("CONTRIBUTION_TOTAL", **total_signal)

        if username:
            G.add_edge(
                f"USERNAME:{username}",
                "CONTRIBUTION_TOTAL",
                relation="TOTAL_CONTRIBUTIONS",
            )

        for y in contrib_years:
            G.add_edge(
                "CONTRIBUTION_TOTAL",
                f"CONTRIBUTIONS_YEAR:{y['meta']['year']}",
                relation="YEARLY",
            )

    # -------------------------
    # Weekday / weekend pattern
    # -------------------------
    pattern_signal = next(
        (s for s in signals if s["signal_type"] == "CONTRIBUTION_TIME_PATTERN"), None
    )

    if pattern_signal:
        G.add_node("CONTRIBUTION_TIME_PATTERN", **pattern_signal)

        if total_signal:
            G.add_edge(
                "CONTRIBUTION_TOTAL",
                "CONTRIBUTION_TIME_PATTERN",
                relation="PATTERN_REL",
            )

    # -------------------------
    # Hourly contributions
    # -------------------------
    hourly_signal = next(
        (s for s in signals if s["signal_type"] == "CONTRIBUTION_HOURLY_PATTERN"), None
    )

    if hourly_signal:
        hourly_counts = hourly_signal.get("value", {})
        prev_hour_node = None

        for h in range(24):
            node_id = f"CONTRIBUTION_HOUR:{h}"
            G.add_node(
                node_id,
                count=hourly_counts.get(str(h), 0),
                signal_type="CONTRIBUTION_HOURLY_PATTERN",
            )

            if prev_hour_node:
                G.add_edge(prev_hour_node, node_id, relation="HOUR_NEXT")

            prev_hour_node = node_id

        if total_signal:
            G.add_edge(
                "CONTRIBUTION_TOTAL",
                "CONTRIBUTION_HOUR:0",
                relation="HOURLY_PATTERN_START",
            )

    # -------------------------
    # Daily contributions
    # -------------------------
    daily_signal = next(
        (s for s in signals if s["signal_type"] == "CONTRIBUTIONS_YEARLY_DATES"), None
    )

    if daily_signal:
        for d in daily_signal["value"]:
            node_id = f"CONTRIBUTION_DAY:{d['date']}"
            G.add_node(
                node_id,
                count=d["count"],
                date=d["date"],
                signal_type="CONTRIBUTIONS_YEARLY_DATES",
            )

            if username:
                G.add_edge(
                    f"USERNAME:{username}",
                    node_id,
                    relation="DAILY_CONTRIBUTION",
                )

    # -------------------------
    # Extra profile info
    # -------------------------
    extra_signals = [
        s
        for s in signals
        if s["signal_type"] in ("GITHUB_PAGES", "PROFILE_PLATFORM", "PRONOUNS")
    ]

    for s in extra_signals:
        node_id = f"{s['signal_type']}:{s['value']}"
        G.add_node(node_id, **s)

        if username:
            G.add_edge(
                f"USERNAME:{username}",
                node_id,
                relation="EXTRA_PROFILE_INFO",
            )

    return G


def save_graph_json(path, G):
    if not isinstance(G, nx.Graph):
        raise TypeError("G must be a NetworkX graph")

    if os.path.dirname(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)

    data = json_graph.node_link_data(G)

    with open(path, "w") as f:
        json.dump(data, f, indent=2)


# ============================================================
# 🧠 Neo4j EXPORT
# ============================================================

def export_neo4j_cypher(G, path="graph.cypher"):
    """
    Export the NetworkX graph as Neo4j Cypher statements.
    """

    if not isinstance(G, nx.Graph):
        raise TypeError("G must be a NetworkX graph")

    lines = []

    # Create nodes
    for node_id, attrs in G.nodes(data=True):
        props = {"id": node_id}
        for k, v in attrs.items():
            if isinstance(v, (str, int, float)):
                props[k] = v

        props_str = ", ".join(
            f"{k}: {json.dumps(v)}" for k, v in props.items()
        )
        lines.append(f"MERGE (n:Signal {{{props_str}}});")

    # Create relationships
    for u, v, attrs in G.edges(data=True):
        rel = attrs.get("relation", "RELATED_TO")
        lines.append(
            f"""
MATCH (a:Signal {{id: {json.dumps(u)}}})
MATCH (b:Signal {{id: {json.dumps(v)}}})
MERGE (a)-[:{rel}]->(b);
""".strip()
        )

    if os.path.dirname(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w") as f:
        f.write("\n".join(lines))
