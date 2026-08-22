"""Lab 07 — Memoria de trabajo, episódica y semántica con aislamiento y olvido.

El ejemplo es local y determinista. Enseña contratos de memoria antes de conectar una vector DB:
namespace por usuario, TTL, búsqueda explicable y borrado completo.

Ejecución:
    python modulo-04-agentes/labs/07_memoria_agente.py
"""

from __future__ import annotations

import argparse
import math
import re
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from rich.console import Console
from rich.table import Table

console = Console()
WORD_RE = re.compile(r"[a-z0-9áéíóúüñ]+", re.IGNORECASE)


def terms(text: str) -> set[str]:
    return {token.casefold() for token in WORD_RE.findall(text)}


@dataclass(frozen=True)
class Memory:
    memory_id: str
    namespace: str
    kind: str
    text: str
    created_at: datetime
    expires_at: datetime


class MemoryStore:
    def __init__(self) -> None:
        self._items: dict[str, Memory] = {}

    def remember(self, namespace: str, kind: str, text: str, ttl_days: int = 30) -> Memory:
        if kind not in {"semantic", "episodic"}:
            raise ValueError("kind debe ser semantic o episodic")
        normalized = text.strip()
        if not 3 <= len(normalized) <= 1_000:
            raise ValueError("text debe tener entre 3 y 1000 caracteres")
        if not 1 <= ttl_days <= 365:
            raise ValueError("ttl_days debe estar entre 1 y 365")
        now = datetime.now(UTC)
        memory = Memory(
            memory_id=uuid4().hex,
            namespace=namespace,
            kind=kind,
            text=normalized,
            created_at=now,
            expires_at=now + timedelta(days=ttl_days),
        )
        self._items[memory.memory_id] = memory
        return memory

    def search(self, namespace: str, query: str, limit: int = 3) -> list[tuple[Memory, float]]:
        self.sweep_expired()
        query_terms = terms(query)
        scored = []
        now = datetime.now(UTC)
        for memory in self._items.values():
            if memory.namespace != namespace:
                continue
            memory_terms = terms(memory.text)
            lexical = len(query_terms & memory_terms) / math.sqrt(
                max(1, len(query_terms)) * max(1, len(memory_terms))
            )
            age_days = (now - memory.created_at).total_seconds() / 86_400
            recency = math.exp(-age_days / 30)
            score = 0.85 * lexical + 0.15 * recency
            scored.append((memory, score))
        scored.sort(key=lambda item: item[1], reverse=True)
        return scored[:limit]

    def sweep_expired(self) -> int:
        now = datetime.now(UTC)
        expired = [key for key, memory in self._items.items() if memory.expires_at <= now]
        for key in expired:
            del self._items[key]
        return len(expired)

    def forget_namespace(self, namespace: str) -> int:
        targets = [key for key, memory in self._items.items() if memory.namespace == namespace]
        for key in targets:
            del self._items[key]
        return len(targets)

    def count(self, namespace: str) -> int:
        return sum(memory.namespace == namespace for memory in self._items.values())


class WorkingMemory:
    def __init__(self, max_messages: int = 6) -> None:
        self.max_messages = max_messages
        self.messages: list[str] = []

    def append(self, message: str) -> None:
        self.messages.append(message)
        self.messages = self.messages[-self.max_messages :]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--user", default="tenant-a:user-42")
    parser.add_argument("--query", default="¿Qué formato y proveedor prefiero para los informes?")
    parser.add_argument("--forget", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    store = MemoryStore()
    store.remember(args.user, "semantic", "Prefiere informes breves en Markdown.", ttl_days=90)
    store.remember(args.user, "semantic", "Para ejemplos de API prefiere OpenAI Responses.", ttl_days=90)
    store.remember(args.user, "episodic", "El 18 de agosto aprobó el diseño con citas.", ttl_days=30)
    store.remember("tenant-b:user-42", "semantic", "Prefiere informes extensos en PDF.", ttl_days=90)

    working = WorkingMemory(max_messages=3)
    for message in ("user: hola", "assistant: hola", f"user: {args.query}", "assistant: buscando memoria"):
        working.append(message)

    table = Table(title=f"Memorias recuperadas · {args.user}")
    table.add_column("tipo")
    table.add_column("score")
    table.add_column("texto")
    results = store.search(args.user, args.query)
    for memory, score in results:
        table.add_row(memory.kind, f"{score:.3f}", memory.text)
    console.print(table)
    console.print(f"[dim]Memoria de trabajo ({len(working.messages)}): {working.messages}[/dim]")
    assert all(memory.namespace == args.user for memory, _ in results)

    if args.forget:
        removed = store.forget_namespace(args.user)
        console.print(f"[yellow]Olvido solicitado: {removed} memorias eliminadas.[/yellow]")
        assert store.count(args.user) == 0
    else:
        console.print(
            "[dim]Ejecuta con --forget para probar el borrado por namespace. En producción, "
            "registra consentimiento, propósito, retención y auditoría del borrado.[/dim]"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
