# Module 06 — Loop Engineering

> An agent is not “an LLM with tools.” It is a loop that transforms state under budgets, effects,
> and terminal conditions.

The loop is where errors compound: a mediocre decision changes the state conditioning the next one,
a retry repeats an effect, and an ambiguous observation prevents progress detection. Designing it as
a state machine lets you reason about termination, cost, and recovery before choosing a framework.

## What you will learn

1. Define a transition contract and unambiguous terminal states.
2. Apply simultaneous budgets for steps, time, tokens, cost, and effects.
3. Separate retry, replanning, reflection, and human escalation.
4. Detect stagnation through external progress signals.
5. Make effects idempotent and resume from compatible checkpoints.
6. Evaluate trajectories under failure, cancellation, concurrency, and backpressure.

## Module map

| Step | Reading | Lab | Main evidence |
|---:|---|---|---|
| 1 | [`01-estado-presupuestos-y-terminacion.md`](teoria/01-estado-presupuestos-y-terminacion.md) | [`01_bounded_loop.py`](labs/01_bounded_loop.py) | Every path terminates explainably |
| 2 | [`02-errores-idempotencia-y-reanudacion.md`](teoria/02-errores-idempotencia-y-reanudacion.md) | [`02_durable_loop.py`](labs/02_durable_loop.py) | An accepted effect is not repeated after restart |
| 3 | [`03-progreso-concurrencia-y-evaluacion.md`](teoria/03-progreso-concurrencia-y-evaluacion.md) | Your own tests | More iterations do not substitute for progress |
| 4 | [`ejercicios.md`](ejercicios.md) | Failure injection | Cancellation, exhaustion, and errors preserve valid state |
| 5 | [`proyecto/README.md`](proyecto/README.md) | Integration | The loop can be operated and migrated |

## Terminal states

| State | Meaning | Can it resume? |
|---|---|---|
| `succeeded` | Verified outcome | No; create a new task if the objective changes |
| `failed` | Definitive failure with a cause | Only through an explicit repair transition |
| `exhausted` | Budget consumed | Yes, with new authorization and budget |
| `cancelled` | External signal handled | Yes, when policy and effects permit it |
| `needs_human` | Missing authority or judgement | Yes, by incorporating a signed human decision |

## Proof of work

Deliver a durable loop that:

- stores state and journal after every accepted transition;
- checks budgets before and after an action;
- detects at least one no-progress cycle;
- requires an idempotency key for effects;
- resumes without repeating an existing receipt;
- handles cancellation between steps;
- distinguishes success, impossibility, exhaustion, error, and escalation;
- rejects checkpoints from an incompatible version.

Include tests for every terminal transition and a crash test at the most inconvenient point: after
the external system accepts an effect and before the loop records its receipt.

## Exit criterion

You have completed the module when you can draw the automaton, identify what state persists at every
failure boundary, and prove that no execution remains `running` forever. If control depends on the
model “realizing” something, the loop is not designed yet.

## Primary sources

- [Anthropic — Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)
- [LangGraph — Graph API overview](https://langchain-ai.github.io/langgraph/how-tos/state-reducers/)
- [LangGraph — Interrupts](https://langchain-ai.github.io/langgraph/concepts/breakpoints/)
