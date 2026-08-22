"""Infraestructura didáctica compartida por los labs RAG.

No pretende ser un framework: carga el corpus, crea chunks, ofrece un índice local de embeddings o
un fallback TF-IDF sin descargas y conserva procedencia por chunk.
"""

from __future__ import annotations

import math
import os
import re
import unicodedata
from collections import Counter
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path

import numpy as np

LAB_DIR = Path(__file__).resolve().parent
DATA_DIR = LAB_DIR / "data"
DEFAULT_EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL", "intfloat/multilingual-e5-small"
)
WORD_RE = re.compile(r"[a-z0-9áéíóúüñ]+", re.IGNORECASE)
STOPWORDS = {
    "a", "al", "algo", "como", "con", "cual", "cuando", "de", "del", "donde",
    "el", "ella", "en", "es", "esta", "este", "hay", "la", "las", "le", "lo",
    "los", "para", "por", "que", "se", "si", "su", "sus", "un", "una", "y",
}


@dataclass(frozen=True)
class Document:
    doc_id: str
    title: str
    text: str
    source: str
    metadata: dict[str, str]


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    doc_id: str
    title: str
    text: str
    source: str
    position: int


@dataclass(frozen=True)
class SearchHit:
    chunk: Chunk
    score: float


def parse_front_matter(raw: str) -> tuple[dict[str, str], str]:
    if not raw.startswith("---\n"):
        return {}, raw
    end = raw.find("\n---\n", 4)
    if end < 0:
        return {}, raw
    metadata = {}
    for line in raw[4:end].splitlines():
        key, separator, value = line.partition(":")
        if separator:
            metadata[key.strip()] = value.strip()
    return metadata, raw[end + 5 :].strip()


def load_documents(data_dir: Path = DATA_DIR) -> list[Document]:
    documents = []
    for path in sorted(data_dir.glob("*.md")):
        metadata, text = parse_front_matter(path.read_text(encoding="utf-8"))
        doc_id = metadata.get("doc_id", path.stem)
        title = metadata.get("title", path.stem.replace("-", " ").title())
        documents.append(
            Document(
                doc_id=doc_id,
                title=title,
                text=text,
                source=str(path),
                metadata=metadata,
            )
        )
    if not documents:
        raise FileNotFoundError(f"no hay documentos Markdown en {data_dir}")
    return documents


def normalize_text(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text.casefold())
    return "".join(char for char in decomposed if not unicodedata.combining(char))


def tokenize(text: str) -> list[str]:
    return [
        token
        for token in WORD_RE.findall(normalize_text(text))
        if token not in STOPWORDS
    ]


def fixed_word_chunks(
    documents: Sequence[Document], *, size: int = 140, overlap: int = 30
) -> list[Chunk]:
    if size <= 0 or overlap < 0 or overlap >= size:
        raise ValueError("se requiere size > 0 y 0 <= overlap < size")
    chunks = []
    step = size - overlap
    for document in documents:
        words = document.text.split()
        for position, start in enumerate(range(0, len(words), step)):
            part = words[start : start + size]
            if not part:
                continue
            chunks.append(
                Chunk(
                    chunk_id=f"{document.doc_id}:fixed:{position:03d}",
                    doc_id=document.doc_id,
                    title=document.title,
                    text=" ".join(part),
                    source=document.source,
                    position=position,
                )
            )
            if start + size >= len(words):
                break
    return chunks


def paragraph_chunks(documents: Sequence[Document], *, max_words: int = 180) -> list[Chunk]:
    chunks = []
    for document in documents:
        buffer: list[str] = []
        position = 0
        for paragraph in re.split(r"\n\s*\n", document.text):
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            projected = sum(len(part.split()) for part in buffer) + len(paragraph.split())
            if buffer and projected > max_words:
                chunks.append(
                    Chunk(
                        chunk_id=f"{document.doc_id}:paragraph:{position:03d}",
                        doc_id=document.doc_id,
                        title=document.title,
                        text="\n\n".join(buffer),
                        source=document.source,
                        position=position,
                    )
                )
                position += 1
                buffer = []
            buffer.append(paragraph)
        if buffer:
            chunks.append(
                Chunk(
                    chunk_id=f"{document.doc_id}:paragraph:{position:03d}",
                    doc_id=document.doc_id,
                    title=document.title,
                    text="\n\n".join(buffer),
                    source=document.source,
                    position=position,
                )
            )
    return chunks


def heading_chunks(documents: Sequence[Document], *, max_words: int = 220) -> list[Chunk]:
    chunks = []
    for document in documents:
        current_heading = document.title
        current_lines: list[str] = []
        position = 0

        def flush(heading: str, bound_document: Document = document) -> None:
            nonlocal position, current_lines
            if not current_lines:
                return
            words = " ".join(current_lines).split()
            for start in range(0, len(words), max_words):
                part = words[start : start + max_words]
                if not part:
                    continue
                chunks.append(
                    Chunk(
                        chunk_id=f"{bound_document.doc_id}:heading:{position:03d}",
                        doc_id=bound_document.doc_id,
                        title=f"{bound_document.title} — {heading}",
                        text=f"## {heading}\n" + " ".join(part),
                        source=bound_document.source,
                        position=position,
                    )
                )
                position += 1
            current_lines = []

        for line in document.text.splitlines():
            if line.startswith("## "):
                flush(current_heading)
                current_heading = line[3:].strip()
            elif not line.startswith("# "):
                current_lines.append(line)
        flush(current_heading)
    return chunks


class TfidfEncoder:
    """TF-IDF mínimo para smoke tests offline; no sustituye a embeddings semánticos."""

    def __init__(self, corpus: Iterable[str]) -> None:
        tokenized = [tokenize(text) for text in corpus]
        document_frequency = Counter()
        for terms in tokenized:
            document_frequency.update(set(terms))
        self.vocabulary = {
            term: index for index, term in enumerate(sorted(document_frequency))
        }
        n_docs = len(tokenized)
        self.idf = np.ones(len(self.vocabulary), dtype=np.float32)
        for term, index in self.vocabulary.items():
            self.idf[index] = math.log((n_docs + 1) / (document_frequency[term] + 1)) + 1

    def encode(self, texts: Sequence[str], *, kind: str) -> np.ndarray:
        matrix = np.zeros((len(texts), len(self.vocabulary)), dtype=np.float32)
        for row, text in enumerate(texts):
            counts = Counter(tokenize(text))
            total = sum(counts.values()) or 1
            for term, count in counts.items():
                index = self.vocabulary.get(term)
                if index is not None:
                    matrix[row, index] = (count / total) * self.idf[index]
        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        return matrix / np.where(norms == 0, 1, norms)


class EmbeddingEncoder:
    def __init__(self, model_name: str = DEFAULT_EMBEDDING_MODEL) -> None:
        from sentence_transformers import SentenceTransformer

        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

    def encode(self, texts: Sequence[str], *, kind: str) -> np.ndarray:
        prefix = "query: " if kind == "query" and "e5" in self.model_name.casefold() else "passage: " if "e5" in self.model_name.casefold() else ""
        prepared = [prefix + text for text in texts]
        return np.asarray(
            self.model.encode(
                prepared,
                normalize_embeddings=True,
                show_progress_bar=False,
            ),
            dtype=np.float32,
        )


class SearchIndex:
    def __init__(self, chunks: Sequence[Chunk], *, lexical: bool = False) -> None:
        if not chunks:
            raise ValueError("el índice necesita al menos un chunk")
        self.chunks = list(chunks)
        corpus = [f"{chunk.title}\n{chunk.text}" for chunk in chunks]
        self.encoder = TfidfEncoder(corpus) if lexical else EmbeddingEncoder()
        self.vectors = self.encoder.encode(corpus, kind="passage")

    def search(self, query: str, *, top_k: int = 4) -> list[SearchHit]:
        if top_k <= 0:
            raise ValueError("top_k debe ser > 0")
        query_vector = self.encoder.encode([query], kind="query")[0]
        scores = self.vectors @ query_vector
        indices = np.argsort(-scores)[: min(top_k, len(self.chunks))]
        return [SearchHit(self.chunks[index], float(scores[index])) for index in indices]


def reciprocal_rank_fusion(
    result_sets: Sequence[Sequence[SearchHit]], *, k: int = 60
) -> list[SearchHit]:
    scores: dict[str, float] = Counter()
    chunks: dict[str, Chunk] = {}
    for hits in result_sets:
        for rank, hit in enumerate(hits, start=1):
            scores[hit.chunk.chunk_id] += 1 / (k + rank)
            chunks[hit.chunk.chunk_id] = hit.chunk
    ordered = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    return [SearchHit(chunks[chunk_id], score) for chunk_id, score in ordered]
