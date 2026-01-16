def build_identity_graph(signals):
    nodes = {}
    edges = []

    for s in signals:
        if not isinstance(s, dict):
            continue

        signal_type = s.get("signal_type")
        value = s.get("value")

        if not signal_type or not value:
            continue

        node_id = f"{signal_type}:{value}"

        if node_id not in nodes:
            nodes[node_id] = {
                "id": node_id,
                "type": signal_type,
                "value": value,
            }

    return {
        "nodes": list(nodes.values()),
        "edges": edges,
    }
