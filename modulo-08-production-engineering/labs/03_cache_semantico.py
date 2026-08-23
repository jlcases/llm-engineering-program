"""Lab 03 — Cache semántico con aislamiento, versionado, TTL y umbral calibrable.

La similitud lexical local hace el lab reproducible; en producción se sustituye por embeddings.
Nunca se cachean peticiones marcadas como sensibles y la clave lógica incluye tenant, modelo,
prompt y versión del corpus.

Ejecución:
    python modulo-08-production-engineering/labs/03_cache_semantico.py
"""

from __future__ import annotations

import argparse
import math
import re
import time
from dataclasses import dataclass
from hashlib import sha256

from rich.console import Console
from rich.table import Table

console = Console()
WORD_RE = re.compile(r"[a-z0-9áéíóúüñ]+", re.IGNORECASE)
STOPWORDS = {
    "a", "al", "cómo", "cuánto", "de", "del", "durante", "el", "es", "la", "las",
    "los", "o", "para", "por", "qué", "se", "son", "tiempo", "un", "una", "y",
}


def tokens(text: str) -> set[str]:
    return {
        normalized
        for word in WORD_RE.findall(text)
        if (normalized := word.casefold()) not in STOPWORDS
    }


def cosine_binary(left: str, right: str) -> float:
    a, b = tokens(left), tokens(right)
    return len(a & b) / math.sqrt(max(1, len(a)) * max(1, len(b)))


@dataclass(frozen=True)
class CacheScope:
    tenant: str
    model: str
    prompt_version: str
    corpus_version: str

    @property
    def key(self) -> str:
        raw = f"{self.tenant}\0{self.model}\0{self.prompt_version}\0{self.corpus_version}"
        return sha256(raw.encode()).hexdigest()


@dataclass
class CacheEntry:
    scope_key: str
    question: str
    answer: str
    expires_at: float


class SemanticCache:
    def __init__(self, threshold: float = 0.72) -> None:
        if not 0 < threshold <= 1:
            raise ValueError("threshold debe estar en (0, 1]")
        self.threshold = threshold
        self.entries: list[CacheEntry] = []

    def get(self, scope: CacheScope, question: str) -> tuple[str | None, float]:
        now = time.time()
        self.entries = [entry for entry in self.entries if entry.expires_at > now]
        candidates = [entry for entry in self.entries if entry.scope_key == scope.key]
        if not candidates:
            return None, 0.0
        scored = [(cosine_binary(question, entry.question), entry) for entry in candidates]
        score, entry = max(scored, key=lambda item: item[0])
        return (entry.answer, score) if score >= self.threshold else (None, score)

    def put(
        self,
        scope: CacheScope,
        question: str,
        answer: str,
        *,
        ttl_seconds: int,
        sensitive: bool,
    ) -> bool:
        if sensitive:
            return False
        if not 1 <= ttl_seconds <= 86_400:
            raise ValueError("ttl_seconds debe estar entre 1 y 86400")
        self.entries.append(
            CacheEntry(scope.key, question.strip(), answer.strip(), time.time() + ttl_seconds)
        )
        return True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--threshold", type=float, default=0.72)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    cache = SemanticCache(args.threshold)
    scope = CacheScope("tenant-a", "gpt-5.6-luna", "support-v3", "corpus-2026-08")
    cache.put(
        scope,
        "¿Cuánto dura el enlace para recuperar la contraseña?",
        "El enlace dura 30 minutos.",
        ttl_seconds=300,
        sensitive=False,
    )
    cases = [
        ("paráfrasis", scope, "¿Durante cuánto tiempo es válido el enlace de recuperar contraseña?"),
        ("distinta", scope, "¿Cómo cambio la dirección de facturación?"),
        (
            "otro tenant",
            CacheScope("tenant-b", scope.model, scope.prompt_version, scope.corpus_version),
            "¿Cuánto dura el enlace para recuperar la contraseña?",
        ),
    ]
    table = Table(title=f"Cache semántico · threshold={args.threshold}")
    table.add_column("caso")
    table.add_column("hit")
    table.add_column("score")
    for label, case_scope, question in cases:
        answer, score = cache.get(case_scope, question)
        table.add_row(label, "sí" if answer else "no", f"{score:.3f}")
    console.print(table)
    stored = cache.put(
        scope,
        "Mi tarjeta termina en 4242, ¿por qué falló?",
        "Revisa el estado del método de pago.",
        ttl_seconds=300,
        sensitive=True,
    )
    console.print(f"[dim]Entrada sensible almacenada: {stored}[/dim]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
