import networkx as nx
import json

def build_identity_graph(findings):
    G = nx.Graph()

    # Add GitHub username/email
    for n in findings.get("author_names", []):
        G.add_node(f"username:{n['value']}", type="username")
    for e in findings.get("emails", []):
        G.add_node(f"email:{e['value']}", type="email")
    # Connect usernames to emails
    for n in findings.get("author_names", []):
        for e in findings.get("emails", []):
            G.add_edge(f"username:{n['value']}", f"email:{e['value']}")

    # Add images
    for img in findings.get("images", []):
        G.add_node(f"image:{img['filename']}", type="image")
        # Connect image to usernames (if any)
        for n in findings.get("author_names", []):
            G.add_edge(f"username:{n['value']}", f"image:{img['filename']}")

    # Add username reuse platforms
    for u in findings.get("username_reuse", []):
        node = f"platform_username:{u['site']}"
        G.add_node(node, type="platform")
        if u["found"]:
            for n in findings.get("author_names", []):
                G.add_edge(f"username:{n['value']}", node)

    # Add email reuse
    for e in findings.get("email_reuse", []):
        node = f"platform_email:{e['site']}"
        G.add_node(node, type="platform")
        if e["found"]:
            for em in findings.get("emails", []):
                G.add_edge(f"email:{em['value']}", node)

    return G

def save_graph_json(G, filepath):
    data = nx.node_link_data(G)  # convert graph to JSON serializable format
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)
