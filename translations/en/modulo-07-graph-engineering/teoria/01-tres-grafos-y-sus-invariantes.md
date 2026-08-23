# 01 — Three graphs and their invariants

“We use a graph” does not describe an architecture. You must state what a node represents, what an
edge claims, who may create it, and which query needs to traverse it.

## 1. When a graph is the right structure

Use a graph when variable relationships, paths, neighborhoods, or connectivity matter. Prefer a:

- relational table for known joins and transactional constraints;
- document for aggregates read and written together;
- vector index for semantic similarity;
- graph for changing relationship patterns and multi-hop queries.

A hybrid architecture is normal. The mistake is expecting one store to optimize every query.

## 2. Execution graph

It represents control:

- node: deterministic transformation, model call, tool, or approval;
- edge: transition permitted under a condition;
- state: shared typed snapshot;
- reducer: rule for incorporating updates;
- terminal: explicit stopping condition.

Its invariants include reachable nodes, valid transitions, compatible reducers, cycle limits, and
persistence before an interrupt. Success is measured by outcome and trajectory, not density.

## 3. Knowledge graph

It represents domain claims:

- entity with stable identity;
- type and versioned properties;
- directed semantic relationship;
- event with time and participants;
- alias or mention linked to a resolved entity.

An edge `company_acquired_company` is not equivalent to `mentions`. Define direction, cardinality,
validity, and whether it may coexist with a contradictory relationship.

## 4. Provenance graph

It represents why the system believes or did something:

- source and version;
- exact passage or record;
- normalized claim;
- `supports`, `contradicts`, or `derived_from` relationship;
- decision, actor, and applied policy;
- resulting artifact or effect.

It supports answering “what evidence would change this conclusion?” and retracting claims when a
source is revoked without deleting history.

## 5. Types and identity

Before choosing a database, define:

```text
NodeId = namespace + canonical_key + version_policy
EdgeId = source + predicate + target + valid_time + evidence_set
```

Identity must not depend on model wording. Normalize through business keys, authoritative records,
and deterministic rules. When resolution is uncertain, retain separate mentions and a candidate
relationship with confidence and evidence.

## 6. Useful invariants

- endpoints exist and satisfy permitted types;
- every factual edge has one or more evidence IDs;
- cardinality is checked on write;
- forbidden cycles are detected before commit;
- valid time and recording time are not confused;
- deleting a source invalidates derivatives without deleting audit history;
- a returned path retains every edge and its provenance.

Apply invariants at the write boundary. Asking the generator to “create a coherent graph” does not
protect the system.

## 7. Framework versus conceptual model

LangGraph can run a state graph; Neo4j, Neptune, or an edge table can store knowledge; an event store
can hold provenance. No library defines identity, authority, or truth for you.

Design queries and invariants first. Then choose the engine that executes them with the required
latency, consistency, and cost.
