# Project — Durable research loop

Build a loop that investigates a technical question through several sources, retains evidence, and
ends with an answer, abstention, or escalation. It must survive restarts without repeating downloads
or recorded actions.

## Objective

The system receives a question and must:

- decompose it into verifiable claims;
- search permitted sources within a budget;
- record evidence and contradictions;
- decide whether useful information is missing;
- terminate with citations or calibrated abstention.

Prose style is not evaluated. Control, traceability, and behavior under failure are evaluated.

## Minimum machine

```text
intake -> plan -> acquire -> assess -> answer
                    |         |
                    |         +-> needs_human
                    +-> retry / replan

any running state -> cancelled / exhausted / failed
```

Define state as a versioned schema and every edge as a transition with a guard and reducer.

## Budgets

Control steps, time, tokens, cost, sources consulted, and concurrency. Reserve before fan-out and
reconcile against actual usage. An increase requires an authorization event, not silently mutating
the limit.

## Durability

Persist journal and checkpoint. Every acquisition receives an identity key derived from run, source,
and canonical query. On resumption, reuse receipts or reconcile before calling again.

Test schema compatibility and a migration. A new worker must reject a checkpoint whose permission
meaning has changed.

## Required failures

- 429 with `Retry-After`;
- timeout before sending and after acceptance;
- source that changes version;
- two authorized sources that contradict one another;
- planner repeating the same state;
- cancellation during fan-out;
- crash after persisting intent and before receipt;
- exhausted budget with useful partial evidence.

## Evaluation

Measure outcome, claim coverage, provenance, useful steps, cost per answer, effect duplication,
resumption, and correct escalation. Retain every dimension and segment by failure type.

Include deterministic planners and executors for CI. Model evaluation is an additional layer and
must pin the model, harness, prompts, and seed when one exists.

## Deliverables

- state contract and transition table;
- loop implementation and simulated executors;
- journal, checkpoint, and migration;
- idempotency ledger and reconciliation;
- failure suite and terminal-state tests;
- operational dashboard or report;
- ADR about concurrency and budget;
- crash and resumption demo without duplication.

## Final gate

Stop the process at a randomly selected point across one hundred executions. After resumption, none
may remain `running` forever, exceed its budget without an event, or duplicate a receipt. Document
exceptions as design failures, not “flakiness.”
