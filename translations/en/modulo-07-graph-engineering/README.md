# Module 07 — Graph Engineering

> A graph adds value when relationships are part of the answer or control. If it only changes the
> box diagram, it adds complexity without adding evidence.

This module separates three planes that are often mixed: the execution graph decides which step
happens; the knowledge graph represents domain entities and relationships; the provenance graph
connects claims and decisions to the evidence supporting them. They can collaborate, but they have
different schemas, invariants, and metrics.

## What you will learn

1. Choose among a table, document, vector, and graph according to the query pattern.
2. Design identity, node and edge types, cardinality, and invariants.
3. Model execution with state, reducers, cycles, interrupts, and checkpoints.
4. Build knowledge with entity resolution and temporal evolution.
5. Preserve provenance at claim, relationship, and decision level.
6. Evaluate hybrid retrieval and prove when the graph beats the baseline.

## Module map

| Step | Reading | Lab | Review question |
|---:|---|---|---|
| 1 | [`01-tres-grafos-y-sus-invariantes.md`](teoria/01-tres-grafos-y-sus-invariantes.md) | [`01_typed_provenance_graph.py`](labs/01_typed_provenance_graph.py) | What does every node mean, and which relationship is permitted? |
| 2 | [`02-conocimiento-identidad-y-procedencia.md`](teoria/02-conocimiento-identidad-y-procedencia.md) | Your own tests | What evidence and version support every edge? |
| 3 | [`03-retrieval-hibrido-y-evaluacion.md`](teoria/03-retrieval-hibrido-y-evaluacion.md) | [`02_hybrid_graph_retrieval.py`](labs/02_hybrid_graph_retrieval.py) | Does the path improve a real query? |
| 4 | [`ejercicios.md`](ejercicios.md) | Adversarial cases | How do identity, freshness, or provenance fail? |
| 5 | [`proyecto/README.md`](proyecto/README.md) | Integration | Can the system explain what it knows and what it did? |

## Three planes

| Plane | Typical nodes | Typical edges | Primary metric |
|---|---|---|---|
| Execution | States, tasks, tools | transition, dependency, delegation | termination and transition correctness |
| Knowledge | Entities, events, concepts | belongs to, causes, uses, happened before | relationship precision and coverage |
| Provenance | Claims, sources, versions, decisions | supports, contradicts, derived from | evidence coverage and fidelity |

Do not place all three inside a generic `nodes/edges` table without types. Sharing a storage engine
does not require sharing semantics.

## Proof of work

Deliver a system that:

- validates types, endpoints, and cardinality before writing;
- rejects a relationship without stable evidence;
- resolves two mentions of one entity and retains the decision;
- represents time or version without overwriting history;
- combines textual retrieval with bounded graph expansion;
- returns paths alongside evidence IDs;
- compares precision, coverage, latency, and cost against a graph-free baseline;
- shows one case where the graph hurts and activates a fallback.

## Exit criterion

You have completed the module when you can remove the graph layer, run the same dataset, and explain
with metrics which capability disappears and which cost goes away. If there is no measurable
difference, the graph is not justified.

## Primary sources

- [Microsoft Research — Project GraphRAG](https://www.microsoft.com/en-us/research/project/graphrag/)
- [LangGraph — Graph API overview](https://langchain-ai.github.io/langgraph/how-tos/state-reducers/)
- [LangGraph — Persistence and interrupts](https://langchain-ai.github.io/langgraph/concepts/breakpoints/)
