# Exercises — Loop Engineering

Implement the exercises with a deterministic planner. Then, and only then, connect a model. This
lets you know whether a failure belongs to control or decision-making.

## 1. Transition table

Specify a machine with `running`, `succeeded`, `failed`, `exhausted`, `cancelled`, and `needs_human`.
For every transition declare its event, guard, reducer, and permitted effect.

**Acceptance criteria:**

- there is no implicit transition from a terminal state;
- every `running` state has a next action or alarm;
- incompatible guards fail at build time or in tests;
- terminal reason is mandatory;
- the table generates at least one test per edge.

## 2. Reserved budget

Run two concurrent branches against one shared budget. First reproduce overspend with
check-then-act; then add atomic reservation and reconciliation.

Measure steps, tokens, cost, and capacity. Prove that one branch failure releases only its unconsumed
reservation.

## 3. Progress detector

Define a signature for a test-repair task. Inject two textually different plans that do not change
the set of failing tests.

The loop must detect stagnation, try an alternative policy once, and terminate diagnostically if no
new evidence appears.

## 4. Error matrix

Implement executors returning invalid input, conflict, 429, ambiguous timeout, permission denial,
and invariant bug.

**Acceptance criteria:**

- only transient errors consume retry budget;
- conflict forces a new read before replanning;
- permission denial never enters backoff;
- ambiguous timeout queries a receipt;
- a bug stops the run and emits a structured alert.

## 5. Crash in the critical window

Simulate a provider that accepts an effect and raises an exception before the client receives the
receipt. Restart the loop from the previous checkpoint.

Prove that reconciliation finds the effect by idempotency key and the external counter remains one.

## 6. Checkpoint migration

Create v1 and v2 schemas with a real policy change. Implement a pure migration and cases where
resumption must be rejected.

Deliver versioned fixtures, a round-trip test, rejection of unknown fields, and a decision for runs
that cannot migrate safely.

## 7. Cancellation and compensation

Cancel during a slow action. Distinguish:

1. action not started;
2. interruptible action;
3. accepted effect awaiting a receipt;
4. confirmed effect with possible compensation;
5. irreversible effect.

Compensation must appear as a new action, never as deletion from the journal.

## 8. Operational loop SLO

Define a dashboard and alerts for runs by state, age, terminal reason, resumptions, ambiguous intents,
and useful steps. Include a query detecting `running` without an alarm or pending work.

Trigger an incident and write a short postmortem with initial signal, impact, timeline, cause, and
permanent change.

## Submission

Publish the state diagram or table, code, example journal, v1/v2 checkpoints, happy and adversarial
tests, metrics, and postmortem. Do not include an API key or depend on a provider to run CI.
