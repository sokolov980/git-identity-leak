import json


def build_identity_graph(signals):
    """
    Build a simple node graph from identity signals.
    Output is JSON-compatible for visualization.
    """

    nodes = {}
    edges = []

    for s in signals:
        signal_type = s.get("signal_type")
        value = s.get("value")

        if not signal_type or not value:
            continue

        node_id = f"{signal_type}:{value}"

        if node_id not in nodes:
            nodes[node_id] = {
                "id": node_id,
                "label": value,
                "type": signal_type
            }

    graph = {
        "nodes": list(nodes.values()),
        "edges": edges
    }

    return json.dumps(graph, indent=2)
