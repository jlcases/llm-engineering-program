# 02 — Context, capabilities, and isolation

A harness does not improve by supplying more tokens. It improves when the agent can discover the
right context or capability at the right moment, and when the system prevents that capability from
exceeding the task's authority.

## 1. Legibility before volume

Organize context in layers:

1. **Permanent contract:** purpose, limits, output format, and security policy.
2. **Map:** names and short descriptions of domains, repositories, and capabilities.
3. **On-demand detail:** files, schemas, logs, or metrics requested by a decision.
4. **Run state:** current plan, artifacts, budgets, and latest observation.
5. **Handoff:** structured summary sufficient to resume with a clean window.

The map must support selection without containing the whole manual. If every tool injects all its
documentation into every turn, cost rises and relevant signals compete with inert text.

## 2. Progressive discovery

A public manifest can expose a name, description, effect class, and summarized schema. The harness
provides the complete contract only when a capability enters the candidate set.

```text
task -> capability classes -> candidate manifests -> selected full contract -> invocation
```

Measure the outcome. Progressive discovery is worse if it increases incorrect selections or needs
so many rounds that it exceeds the context savings.

## 3. Authority through four gates

A sensitive call must pass four independent controls:

| Gate | Question | Deterministic control |
|---|---|---|
| Discovery | Should it know this capability? | Task and role filter |
| Invocation | May it call it now? | Allowlist and run state |
| Arguments | What exact scope is requested? | Schema, limits, and identity resolution |
| Effect | May it run without a person? | Policy and single-use approval token |

Hiding a tool is not a security boundary. The boundary belongs in the executor, after resolving
identity, permissions, and scope with server-side data.

## 4. Sandbox and filesystem

For a code task, use a disposable workspace or dedicated worktree. The executor:

- rejects absolute paths and traversal;
- resolves symlinks before checking the root;
- limits size, file count, and process time;
- supplies environment variables through an allowlist;
- separates network, credentials, and filesystem;
- retains only declared artifacts.

A container reduces surface area but does not replace application permissions. A process inside the
container can still delete an entire mounted volume when the volume scope is too broad.

## 5. Isolation between trials

Every trial begins from the same immutable fixture and receives its own directory, cache, and
namespace. Never let the second trial observe:

- artifacts from the first;
- Git history created by an earlier run;
- a cache containing answers or embeddings for the case;
- shared ports, queues, or database rows without partitioning;
- resource limits consumed by another worker.

Contamination can inflate the score or create correlated failures. In either case, you stop measuring
the capability you intended to evaluate.

## 6. Secrets and traces

Do not provide a complete environment-variable store to the process. Supply ephemeral credentials
scoped by resource and action. Redact structurally before serialization: masking with a regular
expression after writing the log is too late.

Record that a credential existed and what permission it represented, not its value. For debugging,
retain request IDs and provider receipts that support correlation without revealing the secret.

## 7. Design checklist

- Does a task enumerate its capabilities and budgets?
- Does the executor recheck authority even when the model chose correctly?
- Is a path validated after resolution?
- Does every trial begin from a provably clean state?
- Can the trace be shared without credentials or personal data?
- Does cleanup run after timeout, cancellation, and crash too?

If an answer depends on “the model usually does not do that,” a harness boundary is missing.
