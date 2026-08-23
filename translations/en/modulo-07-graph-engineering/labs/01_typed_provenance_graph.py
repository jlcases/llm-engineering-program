"""Lab 01 — Typed graph that rejects relationships without provenance.

Run:
    python modulo-07-graph-engineering/labs/01_typed_provenance_graph.py
"""

from __future__ import annotations

import json
from dataclasses import asdict

from _graph_core import Edge, Node, TypedGraph


def build_graph() -> TypedGraph:
    graph = TypedGraph()
    graph.add_node(Node("service:router", "service", {"name": "Model Router"}))
    graph.add_node(Node("model:luna", "model", {"name": "gpt-5.6-luna"}))
    graph.add_node(Node("policy:latency", "policy", {"p95_ms": 1_200}))
    graph.add_edge(Edge("service:router", "selects", "model:luna", ("adr:007",)))
    graph.add_edge(Edge("model:luna", "constrained_by", "policy:latency", ("slo:2026-08",)))
    return graph


def main() -> None:
    graph = build_graph()
    path = graph.shortest_path("service:router", "policy:latency")
    print(json.dumps([asdict(edge) for edge in path], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
