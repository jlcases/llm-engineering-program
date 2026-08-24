"""Baseline RAG local: parsing trazable, TF-IDF, evidencia y abstención."""

from __future__ import annotations

import math
import re
import unicodedata
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

WORD_RE = re.compile(r"[a-z0-9áéíóúüñ]+", re.IGNORECASE)
STOPWORDS = {
    "a", "al", "algo", "como", "con", "cual", "cuando", "de", "del", "donde",
    "el", "ella", "en", "es", "esta", "este", "hay", "la", "las", "le", "lo",
    "los", "para", "por", "que", "se", "si", "su", "sus", "un", "una", "y",
}


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    document_id: str
    title: str
    text: str


@dataclass(frozen=True)
class Hit:
    chunk: Chunk
    score: float


def normalize(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text.casefold())
    return "".join(character for character in decomposed if not unicodedata.combining(character))


def tokenize(text: str) -> list[str]:
    return [token for token in WORD_RE.findall(normalize(text)) if token not in STOPWORDS]


def parse_document(path: Path) -> tuple[str, str, str]:
    raw = path.read_text(encoding="utf-8")
    metadata: dict[str, str] = {}
    body = raw
    if raw.startswith("---\n"):
        boundary = raw.find("\n---\n", 4)
        if boundary >= 0:
            for line in raw[4:boundary].splitlines():
                key, separator, value = line.partition(":")
                if separator:
                    metadata[key.strip()] = value.strip()
            body = raw[boundary + 5 :].strip()
    return (
        metadata.get("doc_id", path.stem),
        metadata.get("title", path.stem.replace("-", " ").title()),
        body,
    )


def section_chunks(corpus_dir: Path, max_words: int = 220) -> list[Chunk]:
    if max_words <= 0:
        raise ValueError("max_words debe ser > 0")
    chunks: list[Chunk] = []
    sources_by_id: dict[str, Path] = {}
    for path in sorted(corpus_dir.glob("*.md")):
        document_id, document_title, body = parse_document(path)
        if not document_id.strip():
            raise ValueError(f"doc_id vacío en {path}")
        if previous := sources_by_id.get(document_id):
            raise ValueError(f"doc_id duplicado {document_id!r}: {previous} y {path}")
        sources_by_id[document_id] = path
        heading = document_title
        lines: list[str] = []
        position = 0

        def flush(
            current_heading: str,
            bound_document_id: str = document_id,
            bound_document_title: str = document_title,
        ) -> None:
            nonlocal lines, position
            words = " ".join(lines).split()
            for start in range(0, len(words), max_words):
                part = words[start : start + max_words]
                if not part:
                    continue
                chunks.append(
                    Chunk(
                        chunk_id=f"{bound_document_id}:section:{position:03d}",
                        document_id=bound_document_id,
                        title=f"{bound_document_title} — {current_heading}",
                        text=" ".join(part),
                    )
                )
                position += 1
            lines = []

        for line in body.splitlines():
            if line.startswith("## "):
                flush(heading)
                heading = line[3:].strip()
            elif not line.startswith("# "):
                lines.append(line)
        flush(heading)
    if not chunks:
        raise FileNotFoundError(f"no se encontró corpus Markdown en {corpus_dir}")
    return chunks


class TfidfRagService:
    pipeline = "tfidf-extractive-v1"

    def __init__(self, corpus_dir: Path) -> None:
        self.chunks = section_chunks(corpus_dir)
        self.document_count = len({chunk.document_id for chunk in self.chunks})
        tokenized = [tokenize(f"{chunk.title} {chunk.text}") for chunk in self.chunks]
        frequencies: Counter[str] = Counter()
        for terms in tokenized:
            frequencies.update(set(terms))
        self.vocabulary = {term: position for position, term in enumerate(sorted(frequencies))}
        total = len(tokenized)
        self.idf = {
            term: math.log((total + 1) / (frequency + 1)) + 1
            for term, frequency in frequencies.items()
        }
        self.vectors = [self._vector(terms) for terms in tokenized]

    def _vector(self, terms: list[str]) -> dict[str, float]:
        counts = Counter(term for term in terms if term in self.vocabulary)
        denominator = sum(counts.values()) or 1
        vector = {
            term: count / denominator * self.idf[term]
            for term, count in counts.items()
        }
        norm = math.sqrt(sum(value * value for value in vector.values())) or 1.0
        return {term: value / norm for term, value in vector.items()}

    @staticmethod
    def _cosine(left: dict[str, float], right: dict[str, float]) -> float:
        common = left.keys() & right.keys()
        return sum(left[term] * right[term] for term in common)

    def search(self, question: str, top_k: int) -> list[Hit]:
        if not question.strip():
            raise ValueError("question no puede estar vacía")
        if isinstance(top_k, bool) or not isinstance(top_k, int) or top_k <= 0:
            raise ValueError("top_k debe ser un entero mayor que cero")
        query = self._vector(tokenize(question))
        scored = [
            Hit(chunk=chunk, score=self._cosine(query, vector))
            for chunk, vector in zip(self.chunks, self.vectors, strict=True)
        ]
        scored.sort(key=lambda hit: hit.score, reverse=True)
        return [hit for hit in scored[:top_k] if hit.score > 0]

    def answer(self, question: str, hits: list[Hit]) -> tuple[str, bool]:
        query_terms = set(tokenize(question))
        candidates: list[tuple[int, float, str, str]] = []
        for hit in hits:
            for sentence in re.split(r"(?<=[.!?])\s+", hit.chunk.text):
                overlap = len(query_terms & set(tokenize(sentence)))
                if overlap:
                    candidates.append((overlap, hit.score, sentence.strip(), hit.chunk.chunk_id))
        if not candidates or not hits or hits[0].score <= 0:
            return "No hay evidencia suficiente en el corpus.", True
        candidates.sort(reverse=True)
        selected = candidates[:2]
        answer = " ".join(f"{sentence} [{chunk_id}]" for _, _, sentence, chunk_id in selected)
        return answer, False
