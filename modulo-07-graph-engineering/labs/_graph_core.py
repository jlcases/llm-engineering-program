"""Grafo tipado y retrieval híbrido offline para los labs de Graph Engineering."""

from __future__ import annotations

import re
from collections import deque
from dataclasses import dataclass, field
from typing import Any

TOKEN_PATTERN = re.compile(r"[a-z0-9]+", re.IGNORECASE)


def tokens(text: str) -> set[str]:
    return {token.casefold() for token in TOKEN_PATTERN.findall(text)}


@dataclass(frozen=True)
class Node:
    node_id: str
    node_type: str
    properties: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Edge:
    source: str
    predicate: str
    target: str
    evidence_ids: tuple[str, ...]


class TypedGraph:
    def __init__(self) -> None:
        self.nodes: dict[str, Node] = {}
        self.edges: list[Edge] = []

    def add_node(self, node: Node) -> None:
        current = self.nodes.get(node.node_id)
        if current and current != node:
            raise ValueError(f"conflicting node identity: {node.node_id}")
        self.nodes[node.node_id] = node

    def add_edge(self, edge: Edge) -> None:
        if edge.source not in self.nodes or edge.target not in self.nodes:
            raise ValueError("edge endpoints must exist")
        if not edge.evidence_ids:
            raise ValueError("every edge requires provenance evidence")
        if edge not in self.edges:
            self.edges.append(edge)

    def outgoing(self, node_id: str, predicate: str | None = None) -> list[Edge]:
        return [
            edge
            for edge in self.edges
            if edge.source == node_id and (predicate is None or edge.predicate == predicate)
        ]

    def shortest_path(self, source: str, target: str, *, max_hops: int = 4) -> list[Edge]:
        if source not in self.nodes or target not in self.nodes:
            return []
        queue: deque[tuple[str, list[Edge]]] = deque([(source, [])])
        visited = {source}
        while queue:
            node_id, path = queue.popleft()
            if len(path) >= max_hops:
                continue
            for edge in self.outgoing(node_id):
                next_path = [*path, edge]
                if edge.target == target:
                    return next_path
                if edge.target not in visited:
                    visited.add(edge.target)
                    queue.append((edge.target, next_path))
        return []


@dataclass(frozen=True)
class EvidenceDocument:
    evidence_id: str
    text: str
    entity_ids: tuple[str, ...]


@dataclass(frozen=True)
class RetrievalResult:
    evidence_ids: tuple[str, ...]
    graph_paths: tuple[tuple[str, str, str], ...]
    provenance_complete: bool


class HybridGraphRetriever:
    def __init__(self, graph: TypedGraph, documents: list[EvidenceDocument]) -> None:
        self.graph = graph
        self.documents = {document.evidence_id: document for document in documents}

    def lexical(self, query: str, *, limit: int = 2) -> list[EvidenceDocument]:
        query_tokens = tokens(query)
        ranked = sorted(
            self.documents.values(),
            key=lambda document: (
                len(query_tokens & tokens(document.text)) / max(len(query_tokens | tokens(document.text)), 1),
                document.evidence_id,
            ),
            reverse=True,
        )
        return ranked[:limit]

    def retrieve(self, query: str, *, source_entity: str, target_entity: str) -> RetrievalResult:
        seeds = self.lexical(query)
        path = self.graph.shortest_path(source_entity, target_entity)
        evidence = {document.evidence_id for document in seeds}
        for edge in path:
            evidence.update(edge.evidence_ids)
        known = tuple(sorted(evidence & self.documents.keys()))
        return RetrievalResult(
            evidence_ids=known,
            graph_paths=tuple((edge.source, edge.predicate, edge.target) for edge in path),
            provenance_complete=bool(path) and all(
                evidence_id in self.documents for edge in path for evidence_id in edge.evidence_ids
            ),
        )
