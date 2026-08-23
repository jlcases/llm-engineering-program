# Project — Operational map with knowledge and provenance

Build a system that answers questions about a product's architecture: which service uses which
model, which policy constrains it, which ADR justified the decision, and which evidence remains
current.

## Target questions

Include at least:

- five factual lookups;
- five relational questions with two or more hops;
- five temporal questions;
- five global or aggregation questions;
- five unanswerable cases or conflicting sources.

Label expected evidence IDs and paths before tuning the system.

## Three graphs

1. **Execution:** ingestion, validation, indexing, and query pipeline.
2. **Knowledge:** services, models, teams, policies, decisions, and relationships.
3. **Provenance:** sources, passages, claims, versions, and derived artifacts.

You may use one engine, but schemas and permissions must remain separate.

## Ingestion

Process ADRs, SLOs, and a fictional service catalog. Retain each source's hash and date, extract
proposals, resolve identity, and validate before commit.

Add a review queue for uncertain relationships. Do not force the model to decide when the signal
falls inside the ambiguous zone.

## Query

Compare four routes: lexical, vector, graph, and hybrid. The response returns:

- text or abstention;
- evidence IDs;
- entity-and-predicate path;
- validity and conflicts;
- truncation signal;
- access-policy version.

## Change and lineage

Correct an ADR, retract a source, and change a policy with retroactive validity. The system must
identify which claims, summaries, and indexes become stale and rebuild only what is necessary.

Retain what the previous version would have answered.

## Adversarial cases

- two entities with the same name;
- an alias changing over time;
- edge without evidence;
- forbidden cycle;
- hub with extreme fan-out;
- stale global summary;
- path crossing a tenant;
- correct seed missing from first-stage retrieval.

## Evaluation

Measure extraction, resolution, evidence recall, path recall, faithfulness, abstention, latency,
cost, fan-out, and invalidation lag. Segment by query type and compare against the baseline.

## Deliverables

- schemas and invariants for the three planes;
- fictional dataset and labels;
- ingestion pipeline with review;
- four retrievers behind a common interface;
- answers with paths and provenance;
- adversarial suite and segmented results;
- lineage and incremental invalidation;
- graph adoption or removal ADR;
- demo of one correction propagating into the answer.

## Final gate

Remove the knowledge graph and rerun the dataset. The defense must show which queries get worse, by
how much, why, and at what cost the improvement was obtained. If you cannot answer those four
questions, the architectural decision is unsupported.
