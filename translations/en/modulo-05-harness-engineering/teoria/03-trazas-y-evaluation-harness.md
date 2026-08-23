# 03 — Traces and the evaluation harness

Evaluating only the final text hides most important failures. An agent can write a correct answer
after modifying the wrong resource, repeating a payment, or querying data it was not authorized to
read.

## 1. Trajectory and outcome

Retain two complementary views:

- **Trajectory:** observable decisions, tool calls, results, errors, and transitions.
- **Outcome:** verifiable environment state when the run ends.

The trajectory explains how it arrived. The outcome confirms whether it actually arrived. Neither
replaces the other.

## 2. Minimum event schema

```json
{
  "run_id": "run-01",
  "sequence": 7,
  "kind": "tool_result",
  "capability": "create_ticket",
  "elapsed_ms": 142,
  "effect_receipt": "ticket:1842",
  "payload_preview": {"status": "created"},
  "policy_version": "effects-v3"
}
```

Use monotonic time for durations and UTC time for external correlation. Sequence must remain stable
even when several tools finish in parallel. Do not persist private reasoning; record decisions,
declared alternatives, and enough evidence to audit behavior.

## 3. Anatomy of an evaluation

A useful evaluation separates:

1. **Task set:** distribution of capabilities and failures that matters to the product.
2. **Fixture:** reproducible initial state.
3. **Trial runner:** harness, model, versions, budgets, and isolation.
4. **Graders:** deterministic rules, model evaluators, and human review where appropriate.
5. **Aggregator:** intervals, segments, and samples, not only an average.
6. **Failure review:** taxonomy that turns failures into concrete changes.

Run multiple trials when variability exists. Report the denominator, dispersion, and exact
environment version; `83 %` without them is decoration.

## 4. Designing independent graders

Combine three classes:

| Grader | Good for | Main risk |
|---|---|---|
| Deterministic | Schema, DB state, tests, permissions, cost | Measuring a proxy that is too narrow |
| Model evaluator | Semantics, coverage, tone, usefulness | Bias, leniency, and non-reproducibility |
| Human | Expert criteria, taste, ambiguous cases | Cost and reviewer variation |

Do not ask the producing agent to assign the only score. When using a judge, calibrate it against
human examples, pin its prompt and version, hide candidate identity, and review disagreements.

## 5. Final result versus process

Score separately:

- outcome success;
- step, token, cost, and latency efficiency;
- permission and approval compliance;
- recovery from injected errors;
- duplicated effects;
- quality of the user-facing response.

An aggregate may serve as a gate, but retain its components. If an optimization gains quality by
duplicating effects, the average must not hide it.

## 6. Negative cases for the harness itself

Test the evaluation infrastructure too:

- a fixture that cannot be created;
- a trial that exceeds timeout and leaves child processes;
- a grader that fails or returns an invalid shape;
- two trials writing the same resource;
- a partial result after cancellation;
- a warm cache that changes the second attempt;
- a trace truncated before the event explaining the failure.

The harness must mark the result as an infrastructure error, not an agent capability failure.
Mixing them contaminates every model or architecture decision.

## 7. From failure to improvement

Classify each failed sample by the responsible boundary: missing context, missing capability,
ambiguous description, incorrect permission, defective executor, uncontrolled loop, faulty grader,
or model limitation. Then repair the system capability, add the case to regression, and rerun the
affected segment plus a canary set.

A useful eval suite accumulates institutional memory. A suite that only produces a number accumulates
charts.
