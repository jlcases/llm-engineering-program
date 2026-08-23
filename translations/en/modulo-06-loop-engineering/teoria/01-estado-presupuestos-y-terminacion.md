# 01 — State, budgets, and termination

The minimum loop observes state, decides, acts, and observes again. The professional version adds a
transition contract, verifiable budgets, and a terminal function that does not depend on optimistic
model text.

## 1. Transition contract

Model every step as:

```text
transition(state, observation, budgets, policy) -> decision
execute(decision) -> action_result
reduce(state, decision, action_result) -> next_state
```

`transition` may use a model. `execute` and `reduce` protect invariants. Separating them lets you
replay a decision, simulate tools, and verify that the reducer rejects an invalid shape.

## 2. Explicit state

State includes only data required to continue:

- run, task, and version identity;
- current objective and constraints;
- latest normalized observation;
- stable artifacts and receipts;
- accumulated budget usage;
- progress marker;
- pending or incorporated human decisions;
- terminal state and reason, when present.

Do not store HTTP clients, connections, or non-serializable objects. Store identity and reconstruct
resources on resumption.

## 3. Multidimensional budget

A single `max_steps` does not constrain a step that opens one hundred processes or spends the entire
token budget. Control at least:

| Dimension | Checked | Terminal signal |
|---|---|---|
| Steps | Before deciding and after accepting a transition | `step_budget` |
| Monotonic time | Before and after every operation | `time_budget` |
| Tokens | When reserving and reconciling actual usage | `token_budget` |
| Cost | With versioned price and actual receipt | `cost_budget` |
| Effects | Before an external write | `effect_budget` |
| Concurrency | When admitting queued work | `capacity_budget` |

Reserve before execution and reconcile afterward. Without reservation, two concurrent actions may
check the same balance and exceed it together.

## 4. Terminal function

Evaluate conditions in a stable order:

1. cancellation or authority revocation;
2. security violation;
3. verified successful outcome;
4. demonstrated impossibility;
5. need for human judgement;
6. exhausted budget;
7. next transition.

Order matters. If a payment was confirmed at the same moment the time budget expired, the outcome
may be success even though the budget is exhausted. Define product semantics and test them.

## 5. Success as external state

Do not accept model-produced `{"done": true}` as the only proof. Query the relevant system:

- the row exists with the expected version;
- the file changed and tests pass;
- the remote ticket returns a receipt;
- the response cites permitted evidence;
- no additional effect occurred.

The model may propose that it finished; the harness verifies the outcome and the loop transitions.

## 6. Impossibility and escalation

An impossible task should not consume budget until it resembles a timeout. Define signals such as a
missing credential, policy conflict, permanently unavailable dependency, or need for a legal
decision. Finish in `failed` or `needs_human` with evidence and concrete options.

Escalation is not asking “what should I do?” Include the minimum state, blocked decision,
alternatives, risk, cost, and exact action a person can authorize.

## 7. Invariants of a bounded loop

- every transition increments a persisted sequence;
- every `running` state has a next action or alarm;
- every budget has a unit, source, and reconciliation policy;
- no terminal state runs another implicit transition;
- every effect has identity before invocation;
- cancellation does not erase evidence of accepted steps.

If you cannot prove these invariants with tests, the loop is a convention, not a control system.
