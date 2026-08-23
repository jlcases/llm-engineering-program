# 02 — Errors, idempotency, and resumption

The hardest failures happen between systems: the provider accepts an action, the network drops
before the response, and the loop does not know whether to repeat it. No prompt resolves that
ambiguity; identity, receipts, and a reconciliation policy do.

## 1. Taxonomy before retry

Classify the error at the boundary that knows it:

| Class | Example | Response |
|---|---|---|
| Invalid input | Incorrect schema or ID | Repair once or fail; no backoff |
| Conflict | Stale version | Read new state and replan |
| Transient | 429 or timeout before sending | Bounded retry with jitter |
| Ambiguous | Timeout after sending | Query by idempotency key |
| Permanent | Permission denied | Fail or escalate; never retry blindly |
| Bug | Impossible shape or broken invariant | Stop, alert, and retain evidence |

The executor returns typed codes. The model must not infer retryability from a human sentence.

## 2. Retry is not replanning

- **Retry:** same intent, arguments, and effect identity.
- **Repair:** corrects invalid input within a small limit.
- **Replan:** changes strategy because world state changed.
- **Reflect:** evaluates evidence and proposes another decision.
- **Escalate:** requests authority or judgement the system does not possess.

Count them separately. An agent that “reasons” ten times about a 403 is only hiding a defective
retry.

## 3. Idempotency key

Derive stable identity from intent, not attempt number:

```text
effect_key = hash(tenant, task_id, effect_type, canonical_arguments, policy_version)
```

The ideal receiving system accepts that key and returns the same receipt. If it does not support one,
create a local intent table and reconcile through a business identifier before repeating.

Idempotency does not mean “running twice is cheap.” It means retrying the same intent produces one
observable effect.

## 4. The ambiguity window

Dangerous sequence:

1. persist a `pending` intent;
2. send the external action;
3. the provider accepts it;
4. the process crashes before persisting the receipt.

On resumption, query first by effect key or business identifier. Send again only if you can prove it
does not exist. When that proof is impossible, finish in `needs_human` instead of gambling with an
irreversible effect.

## 5. Journal and checkpoint

The journal is append-only and records accepted events. The checkpoint is a compact projection for
fast resumption. Retain both:

- the checkpoint answers “where do I continue?”;
- the journal answers “how did I arrive and what must be reconciled?”

Persist event and state in one transaction when they share a database. For external resources,
retain intent, effect key, request ID, and receipt.

## 6. Version compatibility

A checkpoint contains schema, loop, policy, and capability versions. When deploying a new version,
decide explicitly whether to:

- resume unchanged;
- migrate state with a tested function;
- keep the old worker until runs drain;
- cancel and create a new task.

Never deserialize old state and assume silent defaults for permissions or effects.

## 7. Safe cancellation

Cancellation prevents admitting new steps, but it does not magically undo an in-flight effect. Mark
the request, wait or interrupt according to the capability, and reconcile the outcome. If
compensation exists, it is another action with its own identity, permissions, and possible failures.

`cancelled` must retain what completed, what remains uncertain, and what cleanup was scheduled.

## 8. The test that matters

Inject the crash between external acceptance and local persistence. Resume from the last checkpoint
and prove through receipts that the effect exists exactly once. A test that fails only before calling
the tool does not cover the real problem.
