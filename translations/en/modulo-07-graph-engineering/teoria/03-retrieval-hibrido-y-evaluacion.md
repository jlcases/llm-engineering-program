# 03 — Hybrid retrieval and evaluation

The graph does not replace original text. It adds structure for retrieving relationships and global
context, but the answer must return to verifiable evidence.

## 1. Baseline before the graph

First build lexical or vector retrieval and a dataset containing query types:

- local factual;
- one-hop or multi-hop relational;
- global aggregation;
- temporal;
- unanswerable;
- conflicting sources.

The graph is justified only in segments where it improves a product metric or reduces cost or risk.

## 2. Hybrid pipeline

A common strategy:

1. retrieve seeds through text or vectors;
2. map evidence to resolved entities;
3. expand permitted predicates with bounded hops and fan-out;
4. score paths by relevance, authority, freshness, and cost;
5. retrieve passages supporting selected edges;
6. rerank the combined set;
7. answer with evidence IDs and an explainable path.

Do not give the complete subgraph to the model. Budget nodes, edges, tokens, and time.

## 3. Global GraphRAG

For questions about dominant themes or corpus-scale relationships, GraphRAG extracts entities and
relationships, detects communities, and creates hierarchical summaries. It is powerful when local
search cannot aggregate a distributed view.

Indexing cost, extraction sensitivity, and detail loss in summaries require comparison with simpler
alternatives. Do not use it as the default for factual lookup.

## 4. Scoring paths

A function can combine:

```text
path_score = relevance * authority * freshness * provenance_coverage / traversal_cost
```

Avoid multiplying uncalibrated scores without understanding their scale. Begin with interpretable
rules, evaluate, and learn weights only when the dataset supports it.

Penalize long paths, weak predicates, and edges derived from the same source when independent
corroboration is required.

## 5. Metrics

| Layer | Metrics |
|---|---|
| Extraction | mention F1, relation F1, type accuracy |
| Identity | cluster precision/recall, unresolved rate |
| Retrieval | evidence recall@k, path recall, MRR, nDCG |
| Provenance | claims with complete evidence, authorized sources |
| Answer | faithfulness, completeness, correct abstention |
| Operations | latency, expansion, tokens, cost, and invalidation lag |

Compare against the baseline on the same dataset and budget. Report segments and examples where each
system wins.

## 6. Characteristic failures

- **Seed loss:** the correct entity never enters; the graph cannot recover it.
- **Hub explosion:** a popular node consumes fan-out.
- **Wrong merge:** incorrect resolution connects domains that should remain separate.
- **Stale edge:** an expired relationship dominates the path.
- **Circular support:** derived claims cite one another without a primary source.
- **Summary drift:** a global summary survives retraction of its evidence.
- **Permission leak:** expansion crosses an unauthorized edge.

Design a signal and fallback for each one.

## 7. Decide without dogma

Keep the graph when it improves important queries and its gain exceeds indexing, operations, and
risk. Remove it or limit it to one segment when the baseline matches results. Graph Engineering
includes knowing when not to use a graph.
