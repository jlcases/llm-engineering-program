# 05 — Causal benchmarking of harnesses

One task with one bug and a timing table is a smoke test, not a benchmark. It can confirm that a
binary starts and completes a loop, but it cannot establish which mechanism works better or whether
the result will repeat under context pressure, tool failures, or restarts.

A harness benchmark must begin with the claim it is intended to support. Then it must design
controls, tasks, instrumentation, and analysis capable of refuting that claim.

## 1. Three questions, three different designs

| Mode | Valid question | Minimum condition | Scope of the conclusion |
|---|---|---|---|
| **Mechanism** | Which loop or policy handles the same work better? | Same layer, model, protocol, surface, authority, and fixture | Difference attributable to the controlled mechanism |
| **End-to-end outcome** | Which system delivers the better operational result? | Common task and budgets; declared confounders | Complete-system performance under those conditions |
| **Composition** | What does an orchestrator add around a runtime? | Fixed inner runtime and treatment on/off | Incremental gain, cost, and risk of the composition |

Do not change modes after seeing the result. If Aider and Pi use different protocols, their outcome
can be compared, but do not turn the difference into a conclusion about tool-calling reliability. If
Orca launches five agents and the baseline launches one, report best-of-N and total spend: do not
call it a one-to-one comparison.

## 2. Benchmark constitution

Before the first trial, version a document containing:

1. question and permitted claim;
2. task population and sampling strategy;
3. candidates, version, effective configuration, and surface;
4. model, tokenizer, parameters, endpoint, and retry policy;
5. capabilities, schemas, approvals, sandbox, and network;
6. budgets and terminal conditions;
7. primary metrics, secondary metrics, and hard failures;
8. infrastructure exclusions decided before observing results;
9. number of trials, order, seeds, and interval method;
10. artifacts required for independent reproduction.

Recording what was measured afterward allows you to select whichever story looks best. The
constitution turns reasonable changes into visible changes and requires a new edition when they
alter interpretation.

## 3. A suite, not a single task

Include families that exercise different boundaries:

| Family | Capability under test | Failure it must reveal |
|---|---|---|
| Bounded repair | Navigation, editing, and verification | Correct edit without an outcome or out-of-scope diff |
| Change without a test | Evidence design | Claiming success without creating a verifiable regression test |
| Large-repo search | Context selection and retrieval | Indiscriminate reading, lost signal, or invented path |
| Context pressure | Compaction and handoff | Forgotten constraints, repetition, or growing latency |
| Malformed tool call | Parser and recovery policy | Stalled loop, blind retry, or mutated arguments |
| Intermittent tool | Error classification | Retrying a permanent error or abandoning a recoverable one |
| Mid-run restart | Persistence and idempotency | Lost state or duplicated effects |
| Denied permission | Authority control | Bypass, silent escalation, or false success |
| Repository injection | Instruction hierarchy | Exfiltration, out-of-scope change, or dangerous tool use |
| Concurrent work | Isolation | Shared cache, ports, processes, or files |

Each family needs several fixtures and at least one negative case. Publishing every active task makes
overfitting easy; publish the generator, contract, and a sample, then keep a sealed set for the
competitive edition. Results must remain auditable through hashes and later disclosure of the
edition.

## 4. Variables you must fix

For an end-to-end comparison, the lab requires eight explicit controls:

- `task_fixture`: initial state by hash or immutable image;
- `model`: provider, ID, and exact revision;
- `model_parameters`: temperature, sampling, reasoning, and limits;
- `starting_state`: initial history, memory, caches, and files;
- `tool_authority`: manifest, schemas, approvals, and executor permissions;
- `network_policy`: permitted destinations and connection observation;
- `time_budget`: server clock and timeout policy;
- `token_budget`: comparable accounting for input, output, and cache.

Also fix hardware when measuring local latency, execution order, concurrent load, and thermal state.
For remote backends, record region and request IDs, but do not attribute all variation to the harness
when the provider does not offer stable capacity.

## 5. Common instrumentation

Normalize events in the evaluation harness without erasing the original event. Every adapter must
produce at least:

```json
{
  "trial_id": "edition-03/task-041/pi/seed-2",
  "candidate": {"harness": "pi", "version": "pinned", "config_hash": "sha256:..."},
  "model": {"provider": "local", "id": "pinned", "parameters_hash": "sha256:..."},
  "event": {
    "sequence": 18,
    "kind": "tool_result",
    "capability": "run_tests",
    "monotonic_ms": 4821,
    "status": "retryable_error",
    "input_hash": "sha256:...",
    "output_preview": "redacted",
    "effect_receipt": null
  }
}
```

The adapter may map a textual Aider block, a native tool call, or an Orca stage, but it must retain
`raw_event_ref`. If a metric does not exist for a protocol, use `not_applicable`; do not turn it into
zero.

Also record time to first useful action, time to first verifiable outcome, tokens per step, context
size, compaction events, invalid tool calls, retries, human intervention, processes and external
connections, diff, terminal state, and reason.

## 6. Outcomes and failure taxonomy

The final-state grader decides functional success. Then classify separately:

- `agent_failure`: the candidate received a valid trial and failed to achieve the outcome;
- `policy_violation`: it requested or produced an effect outside its authority;
- `harness_failure`: parser, session, persistence, or executor broke the contract;
- `evaluation_infra_error`: fixture, monitor, grader, or cleanup prevents judging the candidate;
- `budget_exhausted`: the run reached a defined limit without a success state;
- `human_abort`: a person stopped the run, retaining the reason.

An infrastructure error is excluded from the capability denominator but included in benchmark
reliability. A policy violation is not offset by speed or a green test: it is a hard failure.

## 7. Metrics without a magic score

Publish components before any aggregate:

1. **Outcome rate:** successes over valid trials, segmented by family.
2. **Harness reliability:** judgeable trials over scheduled trials.
3. **Policy compliance:** runs without violations over valid runs.
4. **Recovery rate:** injected errors recovered from without intervention.
5. **Efficiency conditional on success:** steps, tokens, latency, and cost only among valid outcomes.
6. **Context degradation:** change from start to tail in accuracy, TTFT, and repetition.
7. **Human load:** approvals, clarifications, selection, review, and merge minutes.
8. **Effect integrity:** unique receipts, no duplicates, and confirmed cleanup.

Speed is useful only conditional on correctness and safety. An agent that finishes quickly because it
abandons or skips verification is not efficient. For paired comparisons, report the distribution of
per-task differences and an interval; for rates, show numerator, denominator, and interval. Do not
hide tails behind a mean.

If the product needs a gate, apply hard constraints first and then an explicit function:

```text
eligible = outcome_ok and policy_ok and no_duplicate_effect and trace_complete
utility  = task_value - compute_cost - human_cost - orchestration_cost
```

There is no universal utility. Publish the components so another organization can apply its own
costs and risks.

## 8. Paired design and execution order

Run every fixture with every candidate and randomize order within blocks. A hard task then affects
all candidates and is not confounded with one of them. Alternate candidates to reduce backend drift,
cache warming, and hardware temperature effects.

Trials must start from new clones or images. Do not use `git checkout . && git clean -fd` as the only
guarantee when ignored files, out-of-repository caches, databases, processes, or persistent memory
exist. Compute an initial-state hash and verify cleanup through a post-run inventory.

For nondeterministic systems, execute planned repetitions. A seed does not make a remote provider or
a concurrent scheduler deterministic; it only identifies one condition. Retain every repetition,
not only the best one.

## 9. Architecture-specific tests

### Compaction

Build a phased task with old constraints that become relevant again at the end. Inject long but
irrelevant observations and an error that forces replanning. Compare not only tokens but constraint
retention, discarded evidence, duplication, and TTFT before and after compaction.

### Persistent memory

Use pairs of isomorphic tasks with different data and answers. Audit which entries are written and
what is retrieved. Add a canary that must never persist and a deletion request. The second-pass
benefit counts only if the canary does not return and cleanup is verifiable.

### Parallel orchestration

Fix the inner runtime. Compare one against N using total budget, wall time, selected-candidate
outcome, selection quality, and merge minutes. Include one case where two worktrees change the same
area and another where they share an external service to prove that Git is not the whole sandbox.

### Deterministic workflows

Interrupt after a confirmed effect and resume. The completed stage must not repeat. Change one
role's model without changing the rest, then verify that configuration, commits, and progress log
make the difference attributable.

## 10. Required injected failures

The benchmark's own suite must test:

- truncated tool JSON, extra arguments, and wrong type;
- timeout before and after applying an effect;
- child process that survives its parent;
- output exceeding the limit and containing a secret canary;
- endpoint returning `429`, `500`, an empty response, and a truncated stream;
- expired, reused approval or one bound to different arguments;
- grader that disagrees with the final text;
- partial cleanup and fixture with the wrong hash.

The happy path proves that the benchmark can produce a number. These cases prove whether that number
deserves trust.

## 11. Evidence package

A reproducible edition publishes:

- edition constitution and changelog;
- task generator, open samples, and sealed-set hashes;
- environment images or lockfiles;
- redacted effective configurations and their hashes;
- adapters, event schema, and conformance tests;
- redacted trajectories, outcomes, and final artifacts;
- trial-level results, exclusions, and infrastructure logs;
- analysis script that rebuilds tables from raw data;
- manual review of a sample of successes, failures, and disagreements.

The leaderboard is a derived view, never the source of truth. If you retain only the ranking, you
will not be able to explain a regression when the model, loop, or tool policy changes.

## Exit gate

Your benchmark is ready when a third party can add a harness, run a new task, cause an infrastructure
failure, and obtain the same causal classification without changing the aggregator. They must also
be able to show why Pi–OpenCode is a mechanism comparison, Aider–Pi is an end-to-end comparison with
different protocols, and stablyai Orca–Pi is a composition test.
