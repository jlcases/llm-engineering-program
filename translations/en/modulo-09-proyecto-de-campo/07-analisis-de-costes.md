# Cost Analysis Template

The goal is to explain how much it cost to operate the system, why, how it scales, and which lever would reduce costs without crossing the quality gate. Use real billing/usage data and retain the current applied rate; do not copy figures from a tutorial.

## 1. Period and Economic Unit

Declare:

- UTC period, environment, and commit/digest;
- total requests, successful, aborted, and failed;
- main unit: cost per completed task, not just per call;
- currency and whether taxes are included/excluded;
- date and links for each official rate;
- separate free tiers/credits from actual economic cost.

## 2. Real Breakdown

Fill in with data from the dashboard and invoice:

| Component | Unit | Real Volume | Current Rate | Cost | Source/Evidence |
|---|---|---:|---:|---:|---|
| routing model | input/output tokens | | | | |
| generation model | input/output/reasoning tokens | | | | |
| ingestion embeddings | tokens | | | | |
| query embeddings | tokens | | | | |
| judges/evaluation | calls/tokens | | | | |
| vector DB | storage/operations | | | | |
| API/compute | hours/vCPU/RAM | | | | |
| observability | events/GB | | | | |
| network/egress | GB | | | | |
| monitoring/services | month | | | | |
| **total** | | | | | |

Account for evaluation, retries, and tools: they are part of the product. Show credits in a separate column;
if the provider gifted €20, the observed cost may be 0, but the recurring cost is not.

## 3. Reproducible Formulas

For a single call:

```text
coste_llm =
  input_uncached_tokens / 1_000_000 * tarifa_input
  + cached_input_tokens / 1_000_000 * tarifa_cached_input
  + output_tokens / 1_000_000 * tarifa_output
  + cargos_de_tools
```

For a multi-step task:

```text
coste_tarea = suma(coste_llm de cada intento)
             + embeddings_query
             + búsquedas/reranking
             + tools externas
             + porción de infraestructura y observabilidad

coste_por_tarea_exitosa = coste_total_periodo / tareas_exitosas
```

Do not allocate shared costs by dividing only among requests if batch, ingestion, or evaluation serve a different volume. Explain the chosen driver.

## 4. Distribution, not just mean

Report p50/p95/p99 for tokens, calls, and cost per task. Add:

| Segment/route | tasks | success | p50/p95 tokens | p50/p95 cost | reason |
|---|---:|---:|---:|---:|---|
| cache hit | | | | | |
| Luna/volume | | | | | |
| Terra/balance | | | | | |
| Sol/badge | | | | | |
| tool error/retry | | | | | |
| evaluation | | | | | |

The GPT-5.6 names reflect the August 2026 catalog. If they change, keep the real alias and snapshot from the experiment here; do not rewrite the past with the new name.

## 5. 1×, 10×, and 100× Projections

Separate variable, stepped, and fixed costs:

| Scenario | tasks/month | tokens/task | cache hit | peak concurrency | variable cost | stepped infra | total |
|---|---:|---:|---:|---:|---:|---:|---|
| observed 1× | | | | | | | |
| 10× growth | | | | | | | |
| 100× growth | | | | | | | |
| stress (p95 + retries) | | | | | | | |

Do not multiply everything linearly: an instance jumps in steps, free tiers disappear, discounts/batch may kick in, and rate limits force another architecture. Include a worst-case scenario with long input and an unstable provider.

## 6. Levers and Experiments

For each optimization, calculate the measured savings and loss/risks:

| Lever | Hypothesis | Monthly Savings | Quality Impact | p95 Impact | Evidence | Decision |
|---|---|---:|---:|---:|---|---|
| reduce context | | | | | ablation | |
| semantic cache | | | | | false hits + hit rate | |
| tier routing | | | | | paired eval | |
| batch for eval/ingestion | | | | | bill/run | |
| local model | | | | | total GPU cost | |

An optimization is only promoted if it maintains critical gates. Saving 30% while worsening safety abstention is not savings: it shifts cost to incidents.

## 7. Self-hosting break-even

Compare:

```text
API mensual = volumen_tokens * tarifa_efectiva + herramientas
self-host mensual = GPU + CPU/RAM + disco + egress + observabilidad
                    + horas de operación/guardia + capacidad ociosa
```

Calculate required utilization and throughput, replicas for high availability, and peak reserves.
Include evaluation of the quantized model. A model that fits in VRAM but does not pass the gate is not an
alternative.

## 8. Executive conclusion

Conclude with five figures: total cost, average and p95 cost per successful task, dominant driver,
10× projection, and savings from the next approved lever. Add the greatest risk of the projection and
what signal will alert you that the assumption is no longer holding.
