# Exercises — Graph Engineering

Every exercise begins with the query it must improve. “Use a graph” is not accepted as an objective
without a baseline and removal criterion.

## 1. Typed schema

Model services, models, policies, ADRs, and SLOs. Declare permitted predicates, direction,
cardinality, and required evidence.

**Acceptance criteria:**

- an endpoint of the wrong type is rejected;
- a factual edge without an evidence ID is rejected;
- a repeated ID with incompatible properties fails;
- a tested schema migration exists;
- queries continue working after renaming a display label.

## 2. Resolution with an uncertain zone

Create a dataset of similar names with `same`, `different`, and `unresolved`. Combine an official
key, aliases, and contextual similarity.

Report cluster precision/recall, `unresolved` rate, and review cost. Set the threshold with a cost
function that penalizes a false merge more than leaving two entities separate.

## 3. Bitemporal time

Represent a policy that changes today with retroactive validity. Answer:

1. which policy was valid for an event yesterday;
2. what the system would have answered yesterday with available knowledge;
3. what answer it must produce today about that event.

Include tests preventing history from being overwritten.

## 4. Claim provenance

Build the path source → passage → claim → decision → artifact. Retract one source and propagate the
invalidation.

**Acceptance criteria:**

- the derived artifact is marked stale;
- audit retains the original decision;
- a new build does not use the retracted claim;
- the system lists which elements must be recomputed.

## 5. Multi-hop retrieval

Design twenty relational and twenty factual questions. Compare lexical, vector, graph, and hybrid
retrieval under the same candidate budget.

Report evidence recall, path recall, MRR, latency, and cost by segment. Do not declare a global winner
when query types show different trade-offs.

## 6. Hub explosion

Introduce a node connected to thousands of neighbors. Implement fan-out, predicate, and score
limits, plus a truncation signal visible to the consumer.

Prove that an answer does not present the truncated subgraph as complete.

## 7. Permission leak

Two tenants share a public entity but not their private relationships. Run a query attempting to
cross from the public seed into another tenant's edge.

Authorization must apply at every hop and the trace must retain the policy without revealing the
denied node.

## 8. Removal ADR

Write an ADR covering indexing, operations, invalidation, and evaluation costs. Define the minimum
improvement justifying the graph and a review date.

Include one case where a table or simple hybrid search is the better alternative.

## Submission

Publish the schema, fixtures, evaluator, invariant tests, segmented results, paths with provenance,
and the ADR. Data must be fictional or redistributable and contain no real personal information.
