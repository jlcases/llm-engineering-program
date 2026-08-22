# Módulo 3 — RAG systems y evaluación (2 ECTS · ~55 h)

Retrieval-Augmented Generation es hoy el patrón más desplegado en producción para conectar
LLMs con conocimiento privado o actualizado. Este módulo cubre el pipeline completo —
ingesta, chunking, embeddings, indexado, retrieval, reranking y generación — y, con el mismo
peso, cómo **evaluarlo**: un RAG sin métricas es una demo, no un sistema.

## Objetivos de aprendizaje

Al terminar el módulo deberías ser capaz de:

1. Diseñar la arquitectura de un sistema RAG completo y justificar cada decisión
   (chunking, modelo de embeddings, vector DB, top-k, reranking) con trade-offs reales.
2. Elegir base de datos vectorial según el caso: Pinecone, Weaviate, Qdrant, pgvector,
   Chroma — y saber cuándo NO hace falta una vector DB dedicada.
3. Implementar y comparar estrategias de chunking (fixed, semantic, hierarchical, late
   chunking) midiendo su efecto en retrieval, no por intuición.
4. Añadir reranking con cross-encoders y entender qué aporta ColBERT como término medio.
5. Aplicar técnicas avanzadas (HyDE, multi-query, Self-RAG, CRAG) sabiendo cuándo
   compensan su coste extra.
6. Montar RAG gestionado con Amazon Bedrock Knowledge Bases y saber qué delegas y qué no.
7. Evaluar un pipeline con RAGAS (faithfulness, answer relevancy, context precision/recall)
   y construir datasets de evaluación propios.
8. Detectar y mitigar alucinaciones con métricas y herramientas concretas.
9. Construir una aplicación RAG full-stack (FastAPI + Next.js + vector DB) con evaluación
   automatizada en CI.

## Requisitos previos

- Módulos 1 y 2 completados (API de OpenAI, tokenización, prompting, structured outputs).
- Docker Desktop instalado (para el lab de Qdrant y el proyecto).
- Dependencias del grupo `rag` instaladas desde la raíz del repo:

```bash
uv sync --extra rag
```

RAGAS 0.4.3 no comparte entorno con OpenAI SDK 3.x por una restricción transitiva de
Instructor. La evaluación live usa el entorno aislado descrito en
[`../setup/README.md`](../setup/README.md); los proxies offline no necesitan esa dependencia.

- `.env` en la raíz del repo con `OPENAI_API_KEY` solo para los modos generativos. Los labs
  usan embeddings locales por defecto y ofrecen `--lexical`/`--offline`; únicamente la
  generación y la evaluación RAGAS hacen llamadas de pago.

## Orden de estudio y tiempo estimado (~55 h)

| # | Teoría | Lab asociado | Horas |
|---|--------|--------------|-------|
| 1 | [01 — Arquitectura RAG](teoria/01-arquitectura-rag.md) | — | 4 |
| 2 | [02 — Embeddings y vector DBs](teoria/02-embeddings-y-vector-dbs.md) | [01_embeddings_similitud.py](labs/01_embeddings_similitud.py) | 7 |
| 3 | (repaso 01 + 02) | [02_rag_minimo.py](labs/02_rag_minimo.py) | 4 |
| 4 | [03 — Chunking](teoria/03-chunking.md) | [03_chunking_comparado.py](labs/03_chunking_comparado.py) | 6 |
| 5 | [04 — Reranking](teoria/04-reranking.md) | [04_reranking.py](labs/04_reranking.py) | 5 |
| 6 | [05 — RAG avanzado](teoria/05-rag-avanzado.md) | [05_rag_avanzado_multiquery_hyde.py](labs/05_rag_avanzado_multiquery_hyde.py) | 6 |
| 7 | [06 — Bedrock Knowledge Bases](teoria/06-bedrock-knowledge-bases.md) | — (opcional en AWS) | 3 |
| 8 | [07 — Evaluación con RAGAS](teoria/07-evaluacion-ragas.md) | [06_evaluacion_ragas.py](labs/06_evaluacion_ragas.py) | 6 |
| 9 | [08 — Alucinaciones](teoria/08-alucinaciones.md) | — | 3 |
| 10 | [Ejercicios](ejercicios.md) | Tests y rúbrica de aceptación | 4 |
| 11 | [Proyecto del módulo](proyecto/README.md) | — | 12 |

## Estructura del módulo

```
modulo-03-rag/
├── README.md                  ← estás aquí
├── teoria/                    ← 8 capítulos de teoría
├── labs/                      ← 6 labs ejecutables + corpus en labs/data/
│   └── data/                  ← docs de "NebulaOps" (corpus) + eval_dataset.json
├── ejercicios.md              ← 12 ejercicios con criterios verificables
└── proyecto/                  ← especificación + baseline backend FastAPI probado
```

## El corpus de los labs

Todos los labs trabajan sobre el mismo corpus: la documentación interna ficticia de
**NebulaOps**, una empresa SaaS de observabilidad (handbook, runbooks, políticas, producto,
FAQ). Está en [`labs/data/`](labs/data/) junto con `eval_dataset.json` (preguntas con
ground truth). Usar un corpus común permite comparar técnicas entre labs con las mismas
preguntas.

## Criterio de superación del módulo

- Los 6 labs ejecutados y entendidos (no solo ejecutados).
- Al menos 10 de los 12 ejercicios superan sus criterios de aceptación.
- Proyecto: pipeline RAG completo con score RAGAS medio ≥ 0.75 sobre el dataset de
  evaluación (ver [criterios de aceptación](proyecto/README.md)).
