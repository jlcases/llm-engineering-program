# Project — Verifiable repair harness

Build a harness for an agent that receives a small repository containing a bug, locates the cause,
proposes a change, and proves the repair. The goal is not to maximize autonomy, but to demonstrate
that the environment makes every relevant decision visible and controllable.

## Scenario

Prepare at least twelve tasks distributed across:

- a localized failure with an existing test;
- a failure without a regression test;
- an out-of-scope request;
- an unavailable dependency or service;
- a malicious instruction inside the repository;
- a change that would require an unauthorized external action.

Every task starts from an immutable fixture and runs in a disposable workspace.

Select two runtimes from the same catalog cohort. Then add a compatible orchestrator as an optional
treatment around one of them. Before execution, write down which claim belongs to the mechanism
comparison and which belongs to the composition.

## Edition constitution

Freeze the model, parameters, each runtime version, surface, tool manifest, approvals, sandbox,
network, budgets, and initial state. Publish randomized order, repetitions, metrics, and exclusion
rules before observing results.

The active set will use sealed fixtures. Publish the generator, at least two examples, and hashes for
all cases; disclose the remaining fixtures when the edition closes.

## Minimum architecture

```text
Landscape + Constitution -> Task registry -> Fixture builder
                                                  |
Candidate adapter -> Agent harness -> Isolated workspace + Capability executors
                           |
                           +----------> Normalized trace + Raw event references

Structured trace + Final workspace -> Graders -> Trial report
```

Separate the model behind an interface so CI can run a deterministic planner and an optional
evaluation can run a real one.

## Capabilities

Include reading, searching, editing, and running permitted commands. Model each with:

- a strict schema;
- filesystem or process scope;
- effect class;
- timeout and output limit;
- typed errors;
- approval and retry policy.

Do not expose an arbitrary shell when bounded commands can solve the scenarios. If you choose to
expose it, document why and isolate the process, network, variables, and volume.

## Evaluation

Measure at least:

1. functional outcome;
2. regression across remaining tests;
3. diff within scope;
4. capability and approval compliance;
5. absence of secrets in traces;
6. steps, tokens, latency, and cost;
7. infrastructure errors separated from agent failures;
8. recovery from injected failures and degradation under context pressure;
9. human intervention, effect duplication, and cleanup;
10. incremental cost and selection quality of the orchestration treatment.

Run several trials for nondeterministic cases. Publish intervals and samples, not a number without a
denominator. Interpret speed only among correct and safe trials.

Do not produce one opaque score. Publish outcome rate by family, harness reliability, policy
compliance, recovery rate, and efficiency conditional on success. If you add a utility to order
candidates, retain every component and its units.

## Required adversarial cases

- path traversal and an outward symlink;
- command outside the allowlist;
- process output exceeding the limit;
- timeout with a child process;
- cache or artifact from another trial;
- tool claiming success without producing an outcome;
- attempt to write an external comment without approval;
- restart after a confirmed effect;
- endpoint with a truncated stream and a recoverable error;
- two candidates colliding in Git or a shared service;
- long context in which an initial constraint becomes necessary again at the end.

## Deliverables

- versioned task, capability, trace, and outcome contracts;
- isolated runner with guaranteed cleanup;
- agent harness with a manifest and authority policy;
- evaluation harness with independent graders;
- task suite and infrastructure tests;
- validated catalog, edition constitution, and per-candidate adapters;
- result report and failure taxonomy;
- trial-level data and a script that reconstructs every table;
- ADR about the system's most powerful capability;
- short video in which a happy and adversarial case traverse the same instrumentation.

## Final gate

A reviewer replaces the model with a stub, adds one task, and triggers a tool failure. If they can
locate the problem and repeat the trial without reading the runner's internals, the harness is
legible. If they must interpret free-form logs or clean state manually, it is not finished yet.

As a final defense, that person must change a Pi–OpenCode comparison to Pi–Aider and then to
Pi–Orca(stablyai). The system must change the claim scope or reject it without modifying the
aggregator. That behavior proves the benchmark preserves causality, not only numbers.
