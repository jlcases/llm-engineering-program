# 02 — Knowledge, identity, and provenance

Extracting entities with an LLM is easy. Maintaining a graph that does not merge different people,
does not present expired relationships as current, and supports auditing every claim is the
engineering part.

## 1. Knowledge pipeline

Separate stages and retain their outputs:

1. source ingestion and versioning;
2. segmentation with stable IDs;
3. extraction of mentions and candidate relationships;
4. normalization of types and predicates;
5. entity resolution;
6. invariant validation;
7. commit and index refresh;
8. evaluation on a labeled set.

Do not write model JSON directly into the canonical graph. Treat it as an untrusted proposal.

## 2. Entity resolution

Use signals in authority order:

- official identifier or business key;
- deterministic combination of stable attributes;
- reviewed alias dictionary;
- calibrated contextual similarity;
- human decision for the ambiguous interval.

Define three outcomes: `same`, `different`, and `unresolved`. Always forcing a merge turns visible
uncertainty into silent corruption.

## 3. Claims, not truth blobs

Represent a claim as an object:

```json
{
  "claim_id": "claim:router:selects:luna:2026-08",
  "subject": "service:router",
  "predicate": "selects",
  "object": "model:luna",
  "valid_from": "2026-08-01",
  "valid_to": null,
  "evidence_ids": ["adr:007"],
  "status": "asserted"
}
```

Two sources may support and contradict the same claim. Do not resolve conflict with embedding score;
apply domain authority, freshness, and policy.

## 4. Bitemporal time

Distinguish:

- **valid time:** when the relationship was true in the world;
- **transaction time:** when the system learned or recorded it.

If a policy published today corrects validity beginning yesterday, the two times differ. This
separation lets you reproduce what the system would have answered with knowledge available on a
given date.

## 5. Decision provenance

Link the knowledge path to the decision:

```text
source -> passage -> claim -> graph path -> retrieved context -> decision -> effect
```

Every hop records its version and transformation. If a community summary participates, link it to
the claims that generated it and mark its algorithm and date.

## 6. Correction and retraction

Do not delete a published edge as though it never existed. Record supersession or invalidation,
update read indexes, and retain audit history. Propagate the change to derived claims, summaries, and
materialized answers.

A system without lineage does not know what to recompute when a source changes.

## 7. Extraction and resolution evaluation

Measure separately:

- mention precision and recall;
- type precision;
- relationship F1 by predicate;
- entity-cluster precision and recall;
- provenance coverage;
- freshness and propagated invalidations;
- human-review rate and cost.

Segment by language, length, entity type, and source quality. A high average may hide that the system
merges exactly the names that matter most.

## 8. Security

A graph amplifies correlations. Apply tenant and purpose during the query and every expansion, not
only when selecting seeds. Prevent inference of sensitive attributes through paths even when every
individual node is accessible.

Record which policy authorized every returned path. “The agent found it in the graph” is not an
access basis.
