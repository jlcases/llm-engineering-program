"""Lab 05 — Servidor MCP 2.x de notas, pequeño pero completo.

Expone tools de escritura/búsqueda y un resource de lectura. Los IDs son opacos, las entradas se
validan y las escrituras aceptan clave de idempotencia. No escribe logs en stdout porque rompería
el transporte stdio.

Prueba con Inspector:
    uv run mcp dev modulo-04-agentes/labs/05_mcp_server.py

Arranca por stdio:
    uv run mcp run modulo-04-agentes/labs/05_mcp_server.py
"""

from __future__ import annotations

import hashlib
import logging
import re
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from threading import Lock

from mcp.server import MCPServer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nebula-notes-mcp")
mcp = MCPServer("nebula-notes")

TITLE_RE = re.compile(r"\s+")


@dataclass(frozen=True)
class Note:
    note_id: str
    title: str
    content: str
    created_at: str


class NoteStore:
    def __init__(self) -> None:
        self._notes: dict[str, Note] = {}
        self._idempotency: dict[str, str] = {}
        self._lock = Lock()

    def create(self, title: str, content: str, idempotency_key: str) -> tuple[Note, bool]:
        normalized_title = TITLE_RE.sub(" ", title.strip())
        normalized_content = content.strip()
        if not 2 <= len(normalized_title) <= 120:
            raise ValueError("title debe tener entre 2 y 120 caracteres")
        if not 1 <= len(normalized_content) <= 10_000:
            raise ValueError("content debe tener entre 1 y 10000 caracteres")
        if not 8 <= len(idempotency_key) <= 128:
            raise ValueError("idempotency_key debe tener entre 8 y 128 caracteres")
        with self._lock:
            existing_id = self._idempotency.get(idempotency_key)
            if existing_id:
                return self._notes[existing_id], False
            digest = hashlib.sha256(
                f"{idempotency_key}\0{normalized_title}".encode()
            ).hexdigest()[:16]
            note = Note(
                note_id=digest,
                title=normalized_title,
                content=normalized_content,
                created_at=datetime.now(UTC).isoformat(),
            )
            self._notes[note.note_id] = note
            self._idempotency[idempotency_key] = note.note_id
            return note, True

    def get(self, note_id: str) -> Note:
        note = self._notes.get(note_id)
        if note is None:
            raise ValueError("note_id no existe")
        return note

    def search(self, query: str, limit: int) -> list[Note]:
        terms = set(query.casefold().split())
        scored = []
        for note in self._notes.values():
            haystack = set(f"{note.title} {note.content}".casefold().split())
            score = len(terms & haystack)
            if score:
                scored.append((score, note.created_at, note))
        scored.sort(reverse=True, key=lambda item: (item[0], item[1]))
        return [note for _, _, note in scored[:limit]]


store = NoteStore()


@mcp.tool()
def create_note(title: str, content: str, idempotency_key: str) -> dict:
    """Crea una nota. Repetir la misma idempotency_key devuelve la original sin duplicarla."""
    note, created = store.create(title, content, idempotency_key)
    logger.info("create_note id=%s created=%s", note.note_id, created)
    return {"created": created, "note": asdict(note)}


@mcp.tool()
def search_notes(query: str, limit: int = 5) -> dict:
    """Busca notas por palabras en título y contenido; es una operación de solo lectura."""
    normalized = query.strip()
    if len(normalized) < 2:
        raise ValueError("query debe tener al menos 2 caracteres")
    if not 1 <= limit <= 20:
        raise ValueError("limit debe estar entre 1 y 20")
    notes = store.search(normalized, limit)
    return {
        "count": len(notes),
        "notes": [
            {"note_id": note.note_id, "title": note.title, "created_at": note.created_at}
            for note in notes
        ],
    }


@mcp.resource("notes://{note_id}")
def read_note(note_id: str) -> str:
    """Devuelve una nota completa por su ID opaco."""
    note = store.get(note_id)
    return f"# {note.title}\n\n{note.content}\n\nCreada: {note.created_at}"
