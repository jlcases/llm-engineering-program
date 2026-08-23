# Final Field project Checklist

Mark an item only when linked evidence exists. "Implemented" without a command, result, URL, trace,
or artifact is incomplete. Record the commit and digest of the reviewed version.

## Non-negotiable gates

- [ ] The JTBD works end to end from an interface appropriate for its user.
- [ ] Evidence signals meet precommitted thresholds on a versioned and audited dataset.
- [ ] Every capability executes its happy path and relevant errors with resolvable traces.
- [ ] No prohibited tools or secret/canary leaked in the adversarial suite.
- [ ] Tests, build, and offline eval pass on the delivery commit/digest.

## 1. Architecture

- [ ] Final document with context, negative scope, and measurable RF/RNF requirements.
- [ ] Context, container, and sequence diagrams match the deployed state.
- [ ] Irreversible or costly decisions have an ADR with alternatives and a review signal.
- [ ] Alternatives and trade-offs include results or costs, not just opinions.
- [ ] Threat model with assets, trust boundaries, threats, controls, owners, and tests.
- [ ] Changes from v1 architecture explained.

Evidence: versioned document, accepted/replaced ADRs, and exported diagram.

## 2. RAG

- [ ] Corpus manifest with license/origin, hashes, and parser/chunker/embedding versions.
- [ ] Idempotent incremental ingestion covers high, modification, and low.
- [ ] Dataset has enough coverage per segment, with negatives, paraphrases, and multi-source cases;
  holdout frozen.
- [ ] Retrieval reports recall/MRR/nDCG per tag and latency.
- [ ] Generation uses delimited context, resolvable citations, and abstention.
- [ ] The eval harness stores configuration, case-level detail, cost, and an audit of worst results.
- [ ] One ablation justifies chunking, hybrid, or reranker.
- [ ] Five failures with root cause and prioritized action.

Evidence: dataset/hash, manifest, JSON results, report, and reproducible command.

## 3. Agent

- [ ] Graph/flow with typed state, step limit, timeout, and degraded output.
- [ ] Required capabilities have narrow schemas, least privilege, and structured errors.
- [ ] Writes use idempotency and confirmation linked to arguments/actor/TTL.
- [ ] Retry/backoff distinguishes transient from permanent errors.
- [ ] Checkpointer allows resuming without duplicating side effects.
- [ ] Memory has purpose, isolation, retention, and deletion, or justification for not having it.
- [ ] Evaluation includes success, trajectory, safety, steps, tokens, cost, and p95.
- [ ] Comparison against pipeline or single agent demonstrates that complexity pays off.

Evidence: tests without network and four traces: success, error, attack, and approval/resumption.

## 4. Deployment

- [ ] Multi-stage image, non-root, without `.env`/weights, scanned and with SBOM.
- [ ] Digest-based deployment, external configuration/secrets, and rollback tested in < 5 min.
- [ ] `/health` and `/ready` have distinct contracts and do not make paid calls.
- [ ] CI runs tests/evals before deploying; a failure prevents promotion.
- [ ] Rate limit, auth, timeout, circuit breaker, and per-user/tenant budget.
- [ ] The availability SLO and window are justified, measured externally, and accompanied by
  explained incidents.
- [ ] Versioned public load: two runs, varied queries, p50/p95/p99, TTFT, and errors.
- [ ] P95 meets the objective defined before measurement.

Evidence: URL, exported monitor, workflow/run, digest, scan/SBOM, and load reports.

## 5. LLMOps

- [ ] Trace IDs link API, graph, tools, retrieval, and model calls.
- [ ] Dashboard covers reliability, latency, quality/safety, usage/cost.
- [ ] Labels have bounded cardinality and the wording passes the canary test.
- [ ] SLI/SLO/error budget are defined with window and exclusions.
- [ ] Burn rate, p95, provider, cost, quality, and security alerts have an owner/runbook.
- [ ] Representative failures were triggered in staging and recovered through their runbooks.
- [ ] An incident/failure produced a new test or case.

Evidence: versioned dashboard/queries, alerts, notifications, and timeline.

## 6. Costs

- [ ] Period, currency, rates/dates/sources, and credits are separated.
- [ ] Actual cost includes inference, embeddings, evals, retries, tools, infrastructure, and observability.
- [ ] Average cost and p95 per successful task; breakdown by route/model/segment.
- [ ] 10×/100× projection separates variable, fixed, and stepped costs and includes stress testing.
- [ ] Chosen optimization has measured savings and quality/latency.
- [ ] Self-host break-even includes idle capacity, HA, and operations.

Evidence: drafted invoice/usage, dashboard export, and calculation sheet/script.

## 7. Demo and review

- [ ] A short and a deep version of the script exist and have both been rehearsed.
- [ ] Happy path, abstention, attack/error, approval, eval, operation, and cost are visible.
- [ ] Recent contingency plan and offline mode; live vs. recorded is distinguishable.
- [ ] Review questions have answers backed by your own data or an explicit pending experiment.
- [ ] Clean profile, zoom, alternative network, status restored, and notifications silenced.
- [ ] Feature freeze; commit, image, prompt, models, and corpus are exactly annotated.

## Third-party reproducibility

- [ ] README is part of a clean checkout and leads to tests + execution in < 30 minutes.
- [ ] `.env.example` documents variables without secret values.
- [ ] Locks present for Python/Node/infra and current versions verified.
- [ ] Licenses for corpus/models/dependencies reviewed.
- [ ] Backup/restore/rollback commands tested and runbooks accessible.

## Release record

Record in the final README: UTC date/time, commit, image digest, URL, prompt version, corpus
hash, models/snapshots, dataset hash, gate results, and location of evidence. Sign the
decision `go`, `conditional go`, or `no-go` with the accepted risks and their owner.
