# Exercises — Module IV

Agents are evaluated by completed tasks and safe trajectories, not by the persuasiveness of their conversation. Preserve traces with redacted sensitive inputs and always test the error path.

## 1. ReAct with recoverable errors

Extend lab 01 with an inventory tool that can return timeout, 404, and 429. Define which errors are retried, how many times, and with what backoff. Create tests where the agent finishes without looping, does not convert an error into data, and explains what could not be verified.

## 2. Idempotency and confirmation

Add a simulated `create_refund` tool. Execution requires server-side confirmation linked to user, invoice, amount, and expiration, in addition to an idempotency key. Simulate that the response is lost after the commit and demonstrate that the retry does not duplicate the refund.

## 3. Graph vs. pipeline

Implement the same task as a linear function and as `StateGraph`. Compare lines, possible states, stability, and operational cost. Choose the pipeline if you do not need branches, pauses, or persistence; justify with requirements, not with framework preference.

## 4. Cycle with stagnation

Add a `(tool, argumentos, resultado)` trace to lab 03. If it repeats twice without new evidence, cut before `max_attempts`. Add final states `ready`, `exhausted`, `stalled` and tests for each transition.

## 5. Human-in-the-loop

Create a graph that interrupts before any write operation. Present to the approver the action, arguments, impact, principal, and TTL. Test approving, rejecting, editing arguments, and resuming the process after restarting using a persistent checkpointer.

## 6. Hardened MCP Server

Extend lab 05 with SQLite storage, tenant-specific namespaces, and a deletion tool that requires an expected version. Add limits, stderr logging, and protocol tests with an MCP client. Demonstrate that one tenant cannot read another's IDs.

## 7. MCP Client

Write a client that connects to the server via stdio, lists tools/resources, calls `create_note`, and reads the resulting resource. Verify version/capabilities during initialize, handle disconnection, and terminate the process even in the event of an exception.

## 8. Evaluated Supervisor

Build 20 tasks with expected paths. Compare a deterministic supervisor and an LLM router in terms of path accuracy, tasks solved, handoffs, tokens, and latency. Penalize both omitting a critical specialist and adding an unnecessary one.

## 9. Adversarial Multi-agent

Have a specialist return a malicious instruction within its report. The supervisor must treat the report as untrusted data, not enable new tools, and preserve provenance. Add a secret canary and measure observable exfiltration.

## 10. Memory Policy

Define by field: purpose, consent, namespace, retention, encryption, access, and deletion. Implement TTL and `forget_user`. Test ID collisions between tenants, stored prompt injection, and export/deletion requests. Do not store full transcripts for convenience.

## 11. Trajectory Evaluation

Create a deterministic evaluator that checks allowed tools, order, arguments, repetitions, confirmations, and final state. Add a judge solely for semantic quality and calibrate its results against 30 human annotations. Report success, security, steps, cost, and p95.

## 12. Mini-project — auditable research agent

Build an agent that investigates a question using at least three capabilities: search within an allowed corpus, read documents, and calculate/verify. It may use a single graph or specialists if the evaluation demonstrates that it compensates.

```text
research-agent/
├── app/                    # grafo, tools, policy y API/CLI
├── mcp_server/             # al menos una capacidad reutilizable
├── eval/
│   ├── dataset.json        # tareas, evidencia y trayectoria esperada
│   ├── evaluate.py
│   └── results.json
├── tests/                  # tools y grafo sin red
├── threat-model.md
└── README.md
```

Minimum gates:

- ≥ 30 tasks, five negative and five adversarial;
- success ≥ 85% and zero prohibited tools in the frozen test;
- step limit, timeout, budget, and degraded output;
- resolvable citations for every audited factual claim;
- human confirmation for any external effect;
- isolated and deletable memory, or explicit justification for not having it;
- comparison against a non-agent pipeline.

The submission is not approved if the agent only works in the prepared demo.
