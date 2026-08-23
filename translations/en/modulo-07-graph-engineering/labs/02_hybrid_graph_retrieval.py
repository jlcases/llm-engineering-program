"""Lab 02 — Lexical retrieval plus a graph path with verifiable provenance.

Run:
    python modulo-07-graph-engineering/labs/02_hybrid_graph_retrieval.py
"""

from __future__ import annotations

import json
from dataclasses import asdict

from _graph_core import Edge, EvidenceDocument, HybridGraphRetriever, Node, TypedGraph


def build_retriever() -> HybridGraphRetriever:
    documents = [
        EvidenceDocument("doc:adr", "The router selects Luna for low-latency traffic.", ("service:router", "model:luna")),
        EvidenceDocument("doc:slo", "The latency policy requires p95 below 1200 ms.", ("model:luna", "policy:latency")),
        EvidenceDocument("doc:noise", "The design system uses a blue primary color.", ("ui:theme",)),
    ]
    graph = TypedGraph()
    for node in [
        Node("service:router", "service"),
        Node("model:luna", "model"),
        Node("policy:latency", "policy"),
        Node("ui:theme", "interface"),
    ]:
        graph.add_node(node)
    graph.add_edge(Edge("service:router", "selects", "model:luna", ("doc:adr",)))
    graph.add_edge(Edge("model:luna", "constrained_by", "policy:latency", ("doc:slo",)))
    return HybridGraphRetriever(graph, documents)


def main() -> None:
    retriever = build_retriever()
    result = retriever.retrieve(
        "Which policy constrains the model selected by the router?",
        source_entity="service:router",
        target_entity="policy:latency",
    )
    print(json.dumps(asdict(result), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
