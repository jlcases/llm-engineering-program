# Learning path — LLM Systems Engineering

> This path does not award hours or impose a calendar. Effort is indicative; the output of every
> module is reproducible proof of work.

The sequence follows real system dependencies, not one provider's taxonomy. You may enter at any
point if you can produce its proof of work and pass the associated negative cases.

## Three stages, nine proofs

| Stage | Modules | Change you must demonstrate |
|---|---|---|
| **Build interfaces** | 01–03 | The model, context, and knowledge are measurable, replaceable components. |
| **Grant capability without losing control** | 04–07 | The agent acts inside a harness, loop, and graphs with explicit invariants. |
| **Operate and defend** | 08–09 | The system preserves quality, cost, and safety under load, change, and failure. |

## 01 — Model interfaces and foundations

Learn enough about the model to design an interface that survives replacing it.

- Transformers, attention, tokenization, and context limits.
- Generation parameters and their measured effect, not folklore.
- OpenAI, Anthropic, and Amazon Bedrock APIs behind a contract you own.
- Streaming, errors, rate limits, token usage, latency, and metadata.
- Model selection through evaluations representative of the task.

**Proof of work:** a multi-provider client that preserves one contract and records tokens, latency,
errors, and model version.

## 02 — Context and output contracts

Stop treating a prompt as magic text: turn it into a versioned interface.

- Instruction hierarchy, delimitation, and context assembly.
- Few-shot examples and observable reasoning without storing private chains of thought.
- Tool calling with strict schemas and explicit errors.
- Structured outputs, validation, bounded repair, and version compatibility.
- Datasets, graders, A/B comparison, and regression gates.
- Instruction injection, untrusted data, and separation of authority.

**Proof of work:** a pipeline that compares two contract versions on the same dataset and blocks a
significant regression in CI.

## 03 — Retrieval Engineering

Build an evidence chain whose failure can be located before blaming the generator.

- Ingestion, normalization, chunking, and metadata with stable identity.
- Embeddings, dense, lexical, and hybrid search.
- Candidate recall, reranking, and the limits of each stage.
- Citations, abstention, freshness, conflict, and indirect-injection defense.
- Separate evaluation of retrieval, grounding, and final response.
- GraphRAG as an option for relational or global questions, not a default.

**Proof of work:** a system with a labeled set, retrieval metrics, verifiable citations,
unanswerable cases, and stage-by-stage failure analysis.

## 04 — Agent and tool interfaces

Define what the model may do before optimizing how many things it attempts.

- The difference between a workflow, an agent, and conventional automation.
- ReAct, plan-execute, evaluator-optimizer, and delegation patterns.
- Small, typed, observable tools with actionable errors.
- MCP capability negotiation, tools, resources, and lifecycle.
- Working, episodic, and semantic memory with retention policies.
- Multi-agent design only when context or authority separation justifies it.
- Human approval and idempotency for external effects.

**Proof of work:** an agent with three tools and its own MCP server that demonstrates permissions,
traces, recoverable errors, and rejection of unauthorized actions.

## 05 — Harness Engineering

The harness is the system around the model that turns general capability into reliable work.

- Boundaries between the model, agent harness, and evaluation harness.
- Legible context: maps, contracts, state, and versioned artifacts.
- Capability manifests and progressive tool discovery.
- Sandboxes, least privilege, allowlists, and approval points.
- Per-task isolated environments, deterministic fixtures, and cleanup.
- Structured traces of inputs, decisions, tools, outcomes, and final state.
- End-to-end evals with tasks, trials, outcomes, and independent graders.
- Harness maintenance: detect entropy, drift, and missing capabilities.

**Proof of work:** a local harness that runs isolated tasks, restricts capabilities, produces a
portable trace, and generates a reproducible eval report.

## 06 — Loop Engineering

A professional loop is not `while True`: it is a control protocol with terminal states.

- Transition contract: state, observation, decision, action, and outcome.
- Simultaneous budgets for steps, time, tokens, cost, and effects.
- Criteria for success, impossibility, exhaustion, cancellation, and human escalation.
- Progress signals and detection of unproductive cycles.
- Error taxonomy, retry budget, backoff, and circuit breakers.
- Idempotency keys, deduplication, and effect semantics.
- Checkpoints, event journal, resumption, and version compatibility.
- Concurrency, backpressure, and result ordering.

**Proof of work:** a durable loop that completes, exhausts budget, cancels, and resumes without
repeating an accepted effect, with tests for every terminal transition.

## 07 — Graph Engineering

Use graphs when relationships are part of the problem, not to add a fashionable dependency.

- Three distinct planes: execution graph, knowledge graph, and provenance graph.
- Nodes, edges, types, cardinality, identity, and invariants.
- State graphs with branches, cycles, checkpoints, and interrupts.
- Entity extraction, identity resolution, and temporal evolution.
- Claims linked to evidence, version, and source authority.
- Hybrid retrieval through text, vectors, neighbors, and budgeted paths.
- Communities and global summaries in the GraphRAG style.
- Coverage, edge precision, path relevance, and provenance metrics.

**Proof of work:** a system that answers a relational query using text and graph evidence, preserves
the provenance of every claim, and compares the result with a graph-free baseline.

## 08 — Production Engineering for LLM systems

Operate the complete system, including everything the model does not control.

- Traces, metrics, logs, and correlation between quality and operations.
- Continuous evaluation, canary datasets, and drift.
- Routing, caching, batching, and cost budgets.
- Containers, deployment, scaling, and local models.
- Latency, availability, quality, and cost SLOs.
- Threat modeling, prompt injection, secrets, and tenant isolation.
- Privacy, auditability, governance, and incident response.

**Proof of work:** a deployed service with a dashboard, alerts, regression evals, cost analysis,
threat model, and a runbook tested through a simulated incident.

## 09 — Field project

Integrate only the complexity you can justify with data and reproducible failures.

- A real problem and user; scope that can be completed.
- Architecture and ADRs recording alternatives and trade-offs.
- Retrieval or external context with provenance.
- An agent with bounded authority inside its harness and loop.
- Graphs only when they measurably improve a query or decision.
- Early deployment to accumulate operational metrics.
- Reproducible demo, postmortem, and technical defense.

**Proof of work:** an executable repository, deployed URL or package, eval dataset, traces,
dashboard, costs, runbook, and a defense including at least one failure that changed the design.

## Optional routes

- **Certifications:** review official blueprints after building the foundations; they do not replace
  proof of work.
- **Contribution:** improve a source, lab, or rubric through a pull request and join its review.
- **Club Quiz:** practice or compete with server time; the ranking measures recall under pressure,
  not engineering evidence.

## Rule for moving forward

Do not move on because you read the final file. Move on when you can show the artifact, run its happy
and adversarial tests, explain a rejected decision, and identify the evidence that would change your
mind.
