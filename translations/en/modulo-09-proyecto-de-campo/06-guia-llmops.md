# LLMOps Field project Guide

The gate is not "having a dashboard": it is the ability to detect, explain, and revert a degradation
in quality, cost, or reliability. Every chart must answer an operational question and link to an
action or runbook.

## 1. Telemetry Contract

Propagate a `trace_id` from the interface through the harness, loop, graph when present, tools,
retrieval, and provider. Each span records:

| Field | Example | Rule |
|---|---|---|
| `trace_id`, `span_id`, `parent_id` | Opaque IDs | Never email/user ID |
| `operation` / `kind` | `retrieve`, `llm`, `tool` | Bounded vocabulary |
| `model` + snapshot | alias/digest used | Required for reproducibility |
| `prompt_version` | `answer-v7` | Immutable hash or version |
| `corpus_version` | manifest hash | Separates retrieval changes |
| `duration_ms`, `ttft_ms` | number | Histogram, not just average |
| `input/output/reasoning_tokens` | number | According to provider metadata |
| `estimated_cost` | currency + versioned rate | Do not hardcode an eternal rate |
| `status`, `error_code`, `attempt` | bounded values | No stack traces to the user |
| `tool_name`, `approved` | allowlist + boolean | No sensitive arguments |
| `eval_sampled` | boolean | Unites production and evaluation |

Do not use prompt, query, tenant, or free-form error as a Prometheus label: they create unlimited cardinality and leak data. Full content can only go to a trace store with defined redaction, encryption, access, and retention. Include a canary test to demonstrate that redaction works.

## 2. Four operational views

### Reliability

- HTTP 2xx/4xx/5xx rate and `task_success`, separated;
- errors/rate limits/timeouts by provider and tool;
- retries, circuit breaker, and queues;
- external uptime and error budget consumption.

A 200 with an empty response or no evidence is a task failure. Define `task_success` with an evaluator or observable feedback, not by copying the HTTP status.

### Latency

- p50/p95/p99 end-to-end;
- TTFT and total time if streaming;
- routing, retrieval, reranking, tools, and generation spans;
- distribution by route/model and cache hit/miss.

Percentiles are calculated in the metrics backend over histograms; do not average p95 values across windows. Log deployments and model changes to correlate cause and effect.

### Quality and safety

- doc/chunk recall in versioned suite;
- faithfulness, relevancy, and abstention in samples;
- invalid citations, prohibited tools, and omitted approval;
- negative feedback rate/segments;
- blocked attacks and guardrail false positives.

Do not run an expensive judge on every request. Sample by risk, segment, and novelty; run offline evals on every PR and a periodic, authorized live suite.

### Usage and cost

- requests, tokens, and cost per model/route/tenant;
- p50/p95 cost per task, not just daily total;
- cache hit rate and estimated avoided cost;
- consumed budget and projection to period end;
- top expensive operations with opaque IDs.

Save the price table used with `valid_from`, source, and currency. If the provider changes prices, historical series must not be silently recalculated.

## 3. SLOs and alerts

Define SLOs before viewing results. Adaptable example:

| SLI | SLO | Window | Explicit Exclusions |
|---|---:|---:|---|
| external availability | ≥ 99 % | 14 days | announced maintenance |
| task success | ≥ 97 % | 7 days | tasks out of scope properly abstained |
| latency | p95 < 3 s | rolling 24 h | batch jobs |
| sampled faithfulness | ≥ 0.75 | last valid suite | non-respondable cases |
| prohibited tools | 0 | always | none |
| cost per query | within own budget | 24 h | authorized backfills |

Minimal alerts:

1. fast/slow burn rate of the error budget;
2. p95 above SLO for two windows;
3. provider rate limits/timeouts;
4. projected spend exceeds 80% and 100% of budget;
5. drop in global or critical segment eval;
6. any prohibited tool, leaked canary, or omitted approval;
7. failed ingestion/indexing or misaligned versioned corpus.

For each alert, document severity, owner, channel, query, threshold, window, runbook, and closure condition. An alert without an owner or action is noise.

## 4. Alert testing

Build a representative failure suite in staging. At minimum, cover latency, dependency, and quality:

- add 800 ms of controlled latency to trigger p95;
- configure an invalid credential/fixture 429 to exercise retry and circuit breaker;
- run the candidate regression dataset to block quality.

Preserve timestamp, capture/query, affected trace IDs, received notification, detection time,
action, recovery, and learning. Do not inject destructive failures in production to obtain
a capture.

## 5. Common Runbook

Every alert must lead to a short workflow:

1. confirm impact with SLI and window, not with an anecdote;
2. identify the first deployment/model/prompt/corpus that changed;
3. open a representative trace and locate the dominant span;
4. contain: rollback, deactivate route/tool, reduce concurrency, or activate fallback;
5. verify recovery with the same signal and a synthetic task;
6. record the timeline and convert the failure into a test/eval.

Separate mitigation from root cause. "We restarted" may restore service, but does not explain why it occurred.

## 6. Operational evidence

- dashboard exported as code or JSON and URL/timestamped captures;
- queries for each panel and definition for each metric;
- representative tested alerts with their notification and runbook;
- one complete trace of success, tool error, abstention, and human intervention;
- drafting/retention policy and canary test;
- SLO/error budget report and deployed version during the window.

In the review, choose an incident and navigate from alert → metric → trace → version → rollback. That
causal chain is worth more than twenty decorative panels.
