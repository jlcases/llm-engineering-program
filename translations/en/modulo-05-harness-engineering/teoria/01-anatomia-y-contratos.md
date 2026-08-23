# 01 — Harness anatomy and contracts

Changing the prompt does not repair an opaque environment. When an agent cannot find a source,
misreads a tool, or cannot verify its work, the problem usually lies in the system mediating between
the model and the world.

## 1. Four parts that must not be mixed

| Part | Responsibility | It should not decide |
|---|---|---|
| **Model** | Proposes decisions from the available context | Real permissions or effect success |
| **Agent harness** | Assembles context, exposes capabilities, runs tools, and maintains state | The truth of a claim without evidence |
| **Product** | Defines authority, UX, policies, and permitted effects | How an internal evaluation is scored |
| **Evaluation harness** | Prepares tasks, isolates trials, records, and applies graders | Which capabilities production receives |

The same model inside two different harnesses is two different agents. The same is true for one
harness with another tool, permission, or context-policy version. A result must therefore pin both
identities.

```text
agent_identity = hash(model_contract, harness_version, capability_manifest, policy_version)
```

## 2. Task contract

An operable task needs more than an instruction:

```json
{
  "task_id": "repair-api-017",
  "instruction": "Repair the failing endpoint and prove the regression is fixed",
  "initial_state": "fixture:v3",
  "allowed_capabilities": ["read_repo", "edit_workspace", "run_tests"],
  "budgets": {"steps": 12, "seconds": 600, "external_effects": 0},
  "success": ["target_test_passes", "full_suite_not_worse", "diff_within_scope"]
}
```

`success` describes verifiable outcomes, not a sentence the agent can claim. If the agent says a test
passes while the process returns a nonzero code, the environment state wins.

## 3. Capability contract

Every capability needs at least:

- a stable name and decision-oriented description;
- strict input and output schemas;
- an effect class: read, reversible write, external write, or irreversible;
- required authority and approval condition;
- timeout, maximum size, typed errors, and retry policy;
- the observation it returns and data that must never enter the trace.

A tool returning free text forces the model to guess whether it succeeded. Prefer:

```json
{"ok": false, "error": {"code": "STALE_VERSION", "retryable": false, "current": 18}}
```

over:

```text
Something went wrong. Try again.
```

## 4. Run and terminal state

Every run must end in an enumerated state. At minimum:

- `succeeded`: the outcome satisfies the contract;
- `failed`: a definitive, diagnosed failure exists;
- `exhausted`: a budget was consumed before completion;
- `cancelled`: an external signal stopped execution;
- `needs_human`: non-delegable authority or judgement is missing.

Do not use `completed` as a synonym for success: an execution can complete its lifecycle while
ending exhausted. The final state retains its reason, budget usage, last evidence, and artifacts.

## 5. Version what changes behavior

Record separately:

1. model and parameters;
2. agent harness version;
3. capability manifest;
4. permission policy;
5. fixtures and environment version;
6. every grader version.

A score increase without this matrix cannot reveal what improved. Do not compare trials when one
could see a file, cache, or commit unavailable to the other.

## 6. Invariants before instructions

An instruction says, “do not write outside the workspace.” An invariant resolves the path, checks
that it belongs to the permitted root, and rejects the call before touching disk. Use instructions to
guide decisions and invariants to protect boundaries.

The design rule is simple: if a condition can be verified deterministically at the boundary, do not
delegate it to the model.
