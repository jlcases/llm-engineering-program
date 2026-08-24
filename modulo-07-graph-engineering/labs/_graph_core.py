"""Grafo tipado y retrieval híbrido offline para los labs de Graph Engineering."""

from __future__ import annotations

import re
from collections import deque
from dataclasses import dataclass, field
from typing import Any

TOKEN_PATTERN = re.compile(r"[^\W_]+", re.UNICODE)


def tokens(text: str) -> set[str]:
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    return {token.casefold() for token in TOKEN_PATTERN.findall(text)}


@dataclass(frozen=True)
class Node:
    node_id: str
    node_type: str
    properties: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.node_id, str) or not self.node_id.strip():
            raise ValueError("node_id cannot be blank")
        if not isinstance(self.node_type, str) or not self.node_type.strip():
            raise ValueError("node_type cannot be blank")
        if not isinstance(self.properties, dict):
            raise TypeError("properties must be an object")


@dataclass(frozen=True)
class Edge:
    source: str
    predicate: str
    target: str
    evidence_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        for name in ("source", "predicate", "target"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} cannot be blank")
        if not isinstance(self.evidence_ids, tuple):
            raise TypeError("evidence_ids must be a tuple")
        if not self.evidence_ids:
            raise ValueError("every edge requires provenance evidence")
        if any(not isinstance(evidence_id, str) or not evidence_id.strip() for evidence_id in self.evidence_ids):
            raise ValueError("evidence IDs cannot be blank")
        if len(set(self.evidence_ids)) != len(self.evidence_ids):
            raise ValueError("evidence IDs on an edge must be unique")


class TypedGraph:
    def __init__(self) -> None:
        self.nodes: dict[str, Node] = {}
        self.edges: list[Edge] = []

    def add_node(self, node: Node) -> None:
        if not isinstance(node, Node):
            raise TypeError("node must be a Node")
        current = self.nodes.get(node.node_id)
        if current and current != node:
            raise ValueError(f"conflicting node identity: {node.node_id}")
        self.nodes[node.node_id] = node

    def add_edge(self, edge: Edge) -> None:
        if not isinstance(edge, Edge):
            raise TypeError("edge must be an Edge")
        if edge.source not in self.nodes or edge.target not in self.nodes:
            raise ValueError("edge endpoints must exist")
        if edge not in self.edges:
            self.edges.append(edge)

    def outgoing(self, node_id: str, predicate: str | None = None) -> list[Edge]:
        return [
            edge
            for edge in self.edges
            if edge.source == node_id and (predicate is None or edge.predicate == predicate)
        ]

    def shortest_path(self, source: str, target: str, *, max_hops: int = 4) -> list[Edge]:
        if isinstance(max_hops, bool) or not isinstance(max_hops, int) or max_hops < 1:
            raise ValueError("max_hops must be greater than zero")
        if not isinstance(source, str) or not isinstance(target, str):
            raise TypeError("source and target must be strings")
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

    def __post_init__(self) -> None:
        if not isinstance(self.evidence_id, str) or not self.evidence_id.strip():
            raise ValueError("evidence ID cannot be blank")
        if not isinstance(self.text, str):
            raise TypeError("evidence text must be a string")
        if not isinstance(self.entity_ids, tuple):
            raise TypeError("entity_ids must be a tuple")
        if any(not isinstance(entity_id, str) or not entity_id.strip() for entity_id in self.entity_ids):
            raise ValueError("entity IDs cannot be blank")
        if len(set(self.entity_ids)) != len(self.entity_ids):
            raise ValueError("entity IDs must be unique")


@dataclass(frozen=True)
class RetrievalResult:
    evidence_ids: tuple[str, ...]
    graph_paths: tuple[tuple[str, str, str], ...]
    provenance_complete: bool


class HybridGraphRetriever:
    def __init__(self, graph: TypedGraph, documents: list[EvidenceDocument]) -> None:
        if not isinstance(graph, TypedGraph):
            raise TypeError("graph must be a TypedGraph")
        if not isinstance(documents, list) or any(
            not isinstance(document, EvidenceDocument) for document in documents
        ):
            raise TypeError("documents must be a list of EvidenceDocument objects")
        self.graph = graph
        if len({document.evidence_id for document in documents}) != len(documents):
            raise ValueError("evidence IDs must be unique")
        self.documents = {document.evidence_id: document for document in documents}

    def lexical(self, query: str, *, limit: int = 2) -> list[EvidenceDocument]:
        if isinstance(limit, bool) or not isinstance(limit, int) or limit < 1:
            raise ValueError("limit must be greater than zero")
        query_tokens = tokens(query)
        if not query_tokens:
            return []
        scored = [
            (
                len(query_tokens & tokens(document.text))
                / max(len(query_tokens | tokens(document.text)), 1),
                document,
            )
            for document in self.documents.values()
        ]
        ranked = sorted(
            (item for item in scored if item[0] > 0),
            key=lambda item: (-item[0], item[1].evidence_id),
        )
        return [document for _, document in ranked[:limit]]

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
                evidence_id in self.documents
                and edge.source in self.documents[evidence_id].entity_ids
                and edge.target in self.documents[evidence_id].entity_ids
                for edge in path
                for evidence_id in edge.evidence_ids
            ),
        )
