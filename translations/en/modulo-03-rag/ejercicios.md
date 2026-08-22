# Exercises — Module III

First, solve using the NebulaOps corpus and preserve configuration, per-case results, and conclusions. A visual improvement in a single query does not count as evidence of global improvement.

## 1. Anatomy of a Failure

Select five incorrect responses from an RAG pipeline. For each, separate: corpus coverage, ingestion, chunking, retrieval, ordering, delivered context, generation, and citation. Propose a test that can falsify your diagnosis before modifying the system.

## 2. Embeddings vs. TF-IDF

Run labs 01 and 03 with TF-IDF and with the multilingual embedding. Compare doc recall@4 and MRR@4 by dataset tag. Add six paraphrases without shared vocabulary and explain where each method wins. Record model, version, and indexing time.

## 3. Evidence-based Chunking

Add a recursive strategy of 100–160 words that respects paragraphs. Evaluate at least four size/overlap combinations. Report number of chunks, p50/p95 of length, recall, MRR, and three concrete failures. Choose a configuration with a declared criterion before the experiment.

## 4. Chunk-level Relevance

Expand `eval_dataset.json` with `relevant_chunk_ids` for ten questions. Calculate precision@k, recall@k, MRR, and nDCG. Contrast these results with document-level recall and document two cases where the correct document does not contain the evidence in the retrieved chunk.

## 5. Two-stage Reranker

Compare `candidate_k` 5, 10, and 20 with `final_k` 3 and 5. Measure quality and p50/p95 latency. Include a baseline without reranking and another with the offline heuristic. Decide whether the cross-encoder compensates and for what type of query.

## 6. Hybrid Retrieval

Combine lexical and semantic ranking using Reciprocal Rank Fusion. Do not sum raw scores from different scales. Tune the `k` parameter for RRF during development and freeze it before the final test.
Analyze queries with identifiers, figures, paraphrases, and negations.

## 7. Multi-query and HyDE

Construct 12 difficult queries and compare baseline, multi-query, HyDE, and both. Save the
expansions. Flag any fabricated claims by HyDE and check if it shifted the correct source.
Add a query budget and a rule to avoid expanding simple questions.

## 8. Calibrated Abstention

Use the `answerable=false` cases to calibrate an abstention rule. Evaluate precision/recall of
detection and the cost of false positives/false negatives. Do not rely solely on the unnormalized
neighbor score: combine retrieval signals, coverage, and an explicit insufficiency response.

## 9. Verifiable Citations

Require a citation for each claim. Implement a verifier that checks: retrieved ID, citation
existence, accessible snippet, and minimum lexical support. Create attacks where the context contains
instructions and where the response cites a real source for an unsupported claim.

## 10. RAGAS Evaluation

Run lab 06 on ten cases with two configurations. Repeat the judgment three times, calculate
the mean and range, and manually review the five worst cases. Estimate calls and cost before executing.
Explain which offline proxies correlate—or do not—with judge metrics.

## 11. Incremental Ingestion

Design stable IDs and a manifest with document hash, parser version, chunker, and embedding.
Implement add, update, and delete without reindexing everything. Test an update that removes an
obsolete policy and demonstrate that it no longer appears in retrieval.

## 12. Project — Evaluated RAG Assistant

Complete the `proyecto/` application with a chat interface, session history, and an evidence panel. It must allow comparing two configurations without changing the final dataset.

Minimum deliverables:

```text
rag-nebulaops/
├── corpus-manifest.json
├── app/                    # API y UI
├── eval/                   # dataset, runner, gates y resultados
├── tests/                  # parsing, retrieval, citas y API sin red
├── docs/architecture.md    # ADRs y modelo de amenazas
└── README.md               # ejecución, límites, coste y decisión
```

Gates:

- doc recall@4 ≥ 0.90 and MRR@4 ≥ 0.85 on the frozen test set;
- zero answers with assertions without a retrieved citation in the audited cases;
- correct abstention in at least 4 of the 5 out-of-corpus cases;
- p95 latency and cost per query measured with an explicit budget;
- reproducible offline tests and no secrets in artifacts;
- written analysis of five failures, including at least one that aggregate metrics hide.

The project is approved based on decision traceability, not on reaching an isolated figure.
