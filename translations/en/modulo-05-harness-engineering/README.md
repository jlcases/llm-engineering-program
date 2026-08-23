# Module 05 — Harness Engineering

> The model proposes. The harness decides what it may see, what it may do, what is recorded, and how
> the result is proven valid.

An agent harness turns a general model into a system able to work inside a specific environment. An
evaluation harness runs comparable tasks, retains trajectories and final states, applies graders,
and aggregates results. Confusing the two creates systems that appear to improve when the test
environment is what actually changed.

## What you will learn

1. Separate the model, agent harness, evaluation harness, and eval suite precisely.
2. Design stable contracts for tasks, capabilities, state, traces, and outcomes.
3. Make context and tools discoverable without flooding the context window.
4. Apply least privilege, per-task isolation, and approval before sensitive effects.
5. Run independent trials and separate agent quality from environment noise.
6. Classify runtimes, integrated products, ADEs, and orchestrators before comparing them.
7. Design causal benchmarks that separate mechanism, end-to-end outcome, and composition.
8. Maintain the harness as a product through versioning, drift, debt, and capability removal.

## Module map

| Step | Reading | Lab | Decision you must be able to defend |
|---:|---|---|---|
| 1 | [`01-anatomia-y-contratos.md`](teoria/01-anatomia-y-contratos.md) | — | What belongs to the model, harness, and product |
| 2 | [`02-contexto-capacidades-y-aislamiento.md`](teoria/02-contexto-capacidades-y-aislamiento.md) | [`01_capability_harness.py`](labs/01_capability_harness.py) | What each run may discover and execute |
| 3 | [`03-trazas-y-evaluation-harness.md`](teoria/03-trazas-y-evaluation-harness.md) | [`02_eval_harness.py`](labs/02_eval_harness.py) | How to compare trials without contamination |
| 4 | [`04-panorama-de-harnesses-actuales.md`](teoria/04-panorama-de-harnesses-actuales.md) | [`03_harness_landscape.py`](labs/03_harness_landscape.py) | Which products compete, compose, or live in another layer |
| 5 | [`05-benchmarking-de-harnesses.md`](teoria/05-benchmarking-de-harnesses.md) | Causal suite | Which claim each comparison actually permits |
| 6 | [`ejercicios.md`](ejercicios.md) | Your own tests | What fails when a boundary breaks |
| 7 | [`proyecto/README.md`](proyecto/README.md) | Integration | Whether the harness improves capability without expanding authority |

## Operational vocabulary

| Concept | Minimum contract |
|---|---|
| **Task** | Instruction, initial state, capabilities, budget, and exit criterion |
| **Capability** | Name, schema, effect, permissions, timeout, and possible errors |
| **Run** | Identity, harness version, state, events, and terminal outcome |
| **Trial** | One isolated run of a task inside an evaluation |
| **Trajectory** | Observable sequence of decisions, calls, results, and transitions |
| **Outcome** | Verifiable environment change, not only the final text |
| **Grader** | Independent function measuring one concrete trial property |

## Proof of work

Deliver a local harness that:

- loads a per-task capability manifest;
- blocks disallowed tools and paths outside the workspace;
- requires approval for one configurable effect;
- redacts secrets before persisting traces;
- runs trials in clean, concurrent environments;
- grades output, final state, and environment leaks separately;
- produces a report containing version, latency, failures, and reviewable samples;
- compares at least two runtimes from the same cohort and one runtime-orchestrator composition;
- keeps facts, hypotheses, effective configuration, and primary sources separate.

The happy path is not enough. You must demonstrate at least: an unknown capability, missing
permission, path traversal, tool failure, excessive output, contaminated fixture, and a grader that
disagrees with the final text.

## Exit criterion

You have completed the module when another person can run the same suite twice and explain what
changed in the agent, what changed in the harness, and what variation belongs to the environment. If
those three causes are still mixed into one score, you do not yet have a reliable harness.

## Primary sources

- [OpenAI — Harness engineering](https://openai.com/index/harness-engineering/)
- [Anthropic — Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
- [Anthropic — Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps)
- [DeepSeek Harness — Architecture](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/architecture.md)
- [Pi Agent Harness](https://github.com/earendil-works/pi)
- [Aider — Edit formats](https://aider.chat/docs/more/edit-formats.html)
