# Exercises — Module V

Work with SLOs, budgets, and reproducible artifacts. “It didn’t fail during my test” does not equate to availability; “the average dropped” does not equate to a p95 improvement.

## 1. Observability Contract

Define a span schema for a RAG/agent pipeline: trace/span/parent IDs, version, latency, tokens, cost, status, retry, and error. Decide which data you will not log, how to redact it, and how long it will be retained. Add a test that fails if a secret canary appears in JSONL.

## 2. SLOs and Alerts

Define SLI/SLO for task success, availability, p95, provider errors, and cost. Construct burn-rate alerts for short/long windows. Distinguish a 200 with a useless response from a real success, and explain which signal is calculated online and which via sampling.

## 3. Distributed Traces

Propagate context from API to retriever, queue, and worker. Simulate retry and demonstrate that it maintains the trace but creates a new span with a link to the attempt. Avoid prompts in baggage/headers. Reconstruct the critical path of a request.

## 4. Calibrated Semantic Cache

Create 100 pairs: equivalent, close but distinct, and unrelated. Choose a threshold on dev and measure precision/recall on test. Segment by tenant/model/prompt/corpus, implement TTL and invalidation, and calculate hit rate, savings, false hits, and p95.

## 5. Model Routing

Evaluate Luna/Terra/Sol —or the current tiers when you run them— on 50 real tasks. Train rules only on dev. Report quality, cost, and latency per route, risk overrides, and regret against the minimum model that would have surpassed the case. Freeze the aliases/snapshots used.

## 6. Batch and concurrency

Compare 1, 4, 16, and 32 concurrent requests. Measure TTFT, p50/p95, throughput, errors, and rate limits.
Implement semaphore, timeout, and backoff with jitter. Decide on a concurrency limit based on
curves, not on the maximum that didn't fail once.

## 7. Regression gate

Expand lab 05 to 100 cases with critical segments. The PR runs offline checks; the live run
is authorized, versioned, and budgeted. Block global regressions/segments and preserve the
artifact even if it fails. Add a case that reproduces a real incident.

## 8. Image and supply chain

Build the multi-arch Docker lab, generate SBOM, scan for CVEs, and sign the image. Compare sizes of
stages. Verify non-root, read-only filesystem, signals, health, and absence of `.env`. Document the
base update process and rollback by digest.

## 9. Local serving

Choose a model installed from the current Ollama catalog. Measure warm/cold start, tokens/s, and
quality before/after quantization on 30 cases. After concurrent load, explain why
local results do not prove that Ollama is a production multi-tenant server.

## 10. LLM threat model

Model assets, trust boundaries, and attackers for RAG + tools. Cover direct/indirect injection,
poisoning, exfiltration, confused deputy, economic DoS, and supply chain. Assign preventive,
detective, and recovery controls; test at least one per critical threat.

## 11. Responsible AI and safety

Create counterfactual pairs and relevant segments for your application. Evaluate outcome and abstention
time with intervals. Write model/system card with intended use, limits, and appeal channels.
Design input/output moderation that does not block legitimate support in favor of abuse.

## 12. Milestone — operating the module system III/IV

Deploy the built RAG or agent, first in staging and then in a justified production environment.

```text
operations/
├── Dockerfile + lock + SBOM
├── deploy/                 # infraestructura/config sin secretos
├── dashboards/             # queries y alertas versionadas
├── eval/                   # gates offline/live
├── runbooks/               # incidentes, rollback, proveedor caído
├── threat-model.md
├── system-card.md
└── cost-report.md
```

Gates:

- non-root image, scanned, pinned by digest, and with tested rollback;
- task success rate and p95 latency under SLO during a declared load test;
- timeout, retry, circuit breaker, rate limit, and per-tenant budget;
- quality, latency, tokens/cost, and error dashboard with no sensitive data;
- eval gate that blocks a simulated regression;
- alarm verified with an injected failure and runbook executed;
- actual cost for the period and 10× projection with assumptions.

Evidence must include timestamps, versions, and results; screenshots without configuration are insufficient.
