# ADR (Architecture Decision Record) Template

An ADR captures **an** architectural decision at the moment it is made: what was decided, among which options, and why. Its value becomes apparent weeks later, when someone (the review board, or you yourself) asks "why didn't you use X?" and the answer is written with the information available at that time.

Rules for the capstone:

- **Sequential numbering** (`ADR-001`, `ADR-002`…) in `02-documento-de-arquitectura/adr/`, one file per decision. ADRs are not edited once accepted: if the decision changes, a new one is written that **replaces** the previous one, and the old one moves to state `reemplazado por ADR-NNN`. This trail is exactly what the review board wants to see.
- **Minimum 2 real alternatives** besides the chosen one. "Alternative: not doing it" does not count. If there were no serious alternatives, it was not an architectural decision.
- **Mandatory negative consequences.** Every choice buys something by paying for something else. An ADR without downsides is marketing.
- Healthy length: half a page to one page. If it exceeds two pages, you are documenting implementation, not a decision.

## Format

```markdown
# ADR-NNN: [decisión en una frase con verbo: "Usar X para Y"]

**Estado:** propuesto | aceptado | reemplazado por ADR-NNN
**Fecha:** AAAA-MM-DD
**Decisores:** [tú; en un equipo real, quiénes]

## Contexto
Qué problema fuerza la decisión y qué restricciones aplican
(presupuesto, plazo, requisitos RNF concretos). 2-4 frases.

## Opciones consideradas
1. Opción A — pros / contras (con números cuando existan)
2. Opción B — pros / contras
3. Opción C — pros / contras

## Decisión
Qué opción se elige y el criterio dominante que inclinó la balanza.

## Consecuencias
- Positivas: …
- Negativas / deuda asumida: …
- Qué señal nos haría revisar esta decisión.
```

---

## Filled Example

# ADR-003: Use managed Qdrant (free tier) as vector DB instead of pgvector or FAISS

**Status:** accepted
**Date:** 2026-08-24
**Decision Makers:** J. Cases

## Context

The RAG pipeline indexes ~14,000 chunks (CTE corpus, ~19M tokens) and must serve retrieval with metadata filtering (basic document, version, section type) within a latency budget of ~300 ms for the retrieval stage (RNF-1: P95 total < 3 s). Capstone infrastructure budget: < €20/month. The API deployment is on Railway, without guaranteed persistent volumes between deploys.

## Options Considered

1. **FAISS in-process** — Pros: minimal latency (< 10 ms, no network), zero cost, zero infrastructure. Cons: no native metadata filtering (would require post-filtering, degrading top-k recall); the index lives in the container's filesystem and Railway recreates it on every deploy, forcing a re-download of the index at startup; no concurrent access from a potential ingestion worker.
2. **pgvector on existing Postgres** — Pros: one less infrastructure component (Postgres already exists for metadata), excellent SQL filtering, backups handled. Cons: in tests with 14k chunks, HNSW recall was equivalent to Qdrant, but the Railway free instance (256 MB RAM) enters swap with the HNSW index loaded; upgrading plan breaks the budget.
3. **Qdrant Cloud free tier (1 GB)** — Pros: native payload filtering within the same ANN query (no post-filtering), persistence independent of API deploys, 1 GB is more than enough for 14k chunks with 1024-dim vectors (~120 MB), latency measured from Railway: p50 45 ms / p95 110 ms. Cons: dependency on a third party and the continuity of its free tier; an added network hop; complex filtering (joins) does not exist.

## Decision

Option 3, Qdrant Cloud. The dominant criterion is **metadata filtering within the ANN search** (RF-4: filter by base document and version), which FAISS does not provide and which pgvector only provides with a Postgres instance that does not fit the budget. The independent persistence of deploys also eliminates the entire class of "cold index after deploy" bugs.

## Consequences

- Positive: retrieval with filters in a single call; re-indexing does not touch the API; the Qdrant dashboard serves as a debugging tool for collections.
- Negative / Assumed Debt: soft vendor lock-in (mitigated: our own retrieval interface `Retriever.search()` is the only point that knows Qdrant); +45 ms of network per query; if the free tier disappears, forced migration (~1 day to pgvector with a paid plan).
- We would revisit this decision if: the corpus exceeds ~500k chunks (the free tier falls short), or if the project moves to full self-hosting due to data requirements (then pgvector or Qdrant on the own cluster).
