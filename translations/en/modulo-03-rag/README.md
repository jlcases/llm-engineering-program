# Module 3 — RAG Systems and Evaluation (2 ECTS · ~55 h)

Retrieval-Augmented Generation is today the most widely deployed production pattern for connecting LLMs with private or up-to-date knowledge. This module covers the complete pipeline — ingestion, chunking, embeddings, indexing, retrieval, reranking, and generation — and, with equal emphasis, how to **evaluate it**: a RAG system without metrics is a demo, not a production system.

## Learning Objectives

By the end of this module, you should be able to:

1. Design a complete RAG system architecture and justify every decision (chunking, embedding model, vector DB, top-k, reranking) with real trade-offs.
2. Select a vector database based on the use case: Pinecone, Weaviate, Qdrant, pgvector, Chroma — and know when a dedicated vector DB is NOT required.
3. Implement and compare chunking strategies (fixed, semantic, hierarchical, late chunking) by measuring their effect on retrieval, not by intuition.
4. Add reranking with cross-encoders and understand what ColBERT offers as a middle ground.
5. Apply advanced techniques (HyDE, multi-query, Self-RAG, CRAG) knowing when they justify their additional cost.
6. Set up a managed RAG with Amazon Bedrock Knowledge Bases and know what to delegate and what to keep in-house.
7. Evaluate a pipeline with RAGAS (faithfulness, answer relevancy, context precision/recall) and build your own evaluation datasets.
8. Detect and mitigate hallucinations using specific metrics and tools.
9. Build a full-stack RAG application (FastAPI + Next.js + vector DB) with automated evaluation in CI.

## Prerequisites

- Modules 1 and 2 completed (OpenAI API, tokenization, prompting, structured outputs).
- Docker Desktop installed (for the Qdrant lab and the project).
- Group dependencies `rag` installed from the repo root:

```bash
uv sync --extra rag
```

RAGAS 0.4.3 does not share an environment with OpenAI SDK 3.x due to a transitive dependency constraint from Instructor. Live evaluation uses the isolated environment described in [`../setup/README.md`](../setup/README.md); offline proxies do not require this dependency.

- `.env` at the repo root with `OPENAI_API_KEY` only for generative modes. Labs use local embeddings by default and offer `--lexical`/`--offline`; only generation and RAGAS evaluation incur paid API calls.

## Study Order and Estimated Time (~55 h)

| # | Theory | Associated Lab | Hours |
|---|--------|----------------|-------|
| 1 | [01 — RAG Architecture](teoria/01-arquitectura-rag.md) | — | 4 |
| 2 | [02 — Embeddings and Vector DBs](teoria/02-embeddings-y-vector-dbs.md) | [01_embeddings_similitud.py](labs/01_embeddings_similitud.py) | 7 |
| 3 | (review 01 + 02) | [02_rag_minimo.py](labs/02_rag_minimo.py) | 4 |
| 4 | [03 — Chunking](teoria/03-chunking.md) | [03_chunking_comparado.py](labs/03_chunking_comparado.py) | 6 |
| 5 | [04 — Reranking](teoria/04-reranking.md) | [04_reranking.py](labs/04_reranking.py) | 5 |
| 6 | [05 — Advanced RAG](teoria/05-rag-avanzado.md) | [05_rag_avanzado_multiquery_hyde.py](labs/05_rag_avanzado_multiquery_hyde.py) | 6 |
| 7 | [06 — Bedrock Knowledge Bases](teoria/06-bedrock-knowledge-bases.md) | — (optional on AWS) | 3 |
| 8 | [07 — Evaluation with RAGAS](teoria/07-evaluacion-ragas.md) | [06_evaluacion_ragas.py](labs/06_evaluacion_ragas.py) | 6 |
| 9 | [08 — Hallucinations](teoria/08-alucinaciones.md) | — | 3 |
| 10 | [Exercises](ejercicios.md) | Tests and acceptance rubric | 4 |
| 11 | [Module Project](proyecto/README.md) | — | 12 |

## Module Structure

```
modulo-03-rag/
├── README.md                  ← estás aquí
├── teoria/                    ← 8 capítulos de teoría
├── labs/                      ← 6 labs ejecutables + corpus en labs/data/
│   └── data/                  ← docs de "NebulaOps" (corpus) + eval_dataset.json
├── ejercicios.md              ← 12 ejercicios con criterios verificables
└── proyecto/                  ← especificación + baseline backend FastAPI probado
```

## The Lab Corpus

All labs operate on the same corpus: the fictional internal documentation of **NebulaOps**, an observability SaaS company (handbook, runbooks, policies, product docs, FAQ). It is located at [`labs/data/`](labs/data/) alongside `eval_dataset.json` (questions with ground truth). Using a shared corpus allows you to compare techniques across labs using the exact same questions.

## Module Pass Criteria

- All 6 labs executed and understood (not just executed).
- At least 10 of the 12 exercises meet their acceptance criteria.
- Project: complete RAG pipeline with an average RAGAS score ≥ 0.75 on the evaluation dataset (see [acceptance criteria](proyecto/README.md)).
