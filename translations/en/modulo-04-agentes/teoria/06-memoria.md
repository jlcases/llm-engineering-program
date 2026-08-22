# 06 — Agent Memory: Working, Episodic, and Semantic

> Associated Lab: [`../labs/07_memoria_agente.py`](../labs/07_memoria_agente.py)

An agent's memory is not an infinite conversation. It is a policy for deciding **what
to retain, where, for how long, and when to retrieve it**. Saving everything increases the cost of every turn,
mixes in irrelevant data, and creates privacy risks; saving nothing forces the user to
repeat themselves. Designing memory is designing selection and forgetting.

## 1. Four Concepts Often Confused

| Concept | Lifetime | Example | Mechanism |
|---|---|---|---|
| Working state | one run | current plan, tool results | `State` from the graph |
| Thread history | one conversation | messages and checkpoints | checkpointer |
| Episodic memory | across conversations | "the user rejected option X" | persistent store |
| Semantic memory | across conversations | retrievable preferences/facts | store + search |

The **context window** is only the space the model receives in a single call. It may contain a selection from the four layers, but it is not memory in itself.

## 2. Working State

Contains what is necessary to complete the current task:

```python
from typing import TypedDict


class AgentState(TypedDict):
    messages: list
    plan: list[str]
    completed_steps: list[str]
    tool_errors: list[dict[str, str]]
    remaining_budget_cents: float
```

Make limits and counters explicit. If the iteration count exists only in a local variable, it disappears when resuming from a checkpoint.

Avoid putting non-serializable objects, HTTP clients, or database connections into the state.
The state is data; dependencies are injected into the node.

## 3. Short-term Memory with Checkpoints

A LangGraph checkpointer saves snapshots by `thread_id`:

```python
from langgraph.checkpoint.memory import InMemorySaver


checkpointer = InMemorySaver()
graph = builder.compile(checkpointer=checkpointer)
config = {"configurable": {"thread_id": "customer-42:conversation-7"}}

graph.invoke(
    {"messages": [{"role": "user", "content": "Mi plan es Nebula Pro"}]},
    config=config,
)
graph.invoke(
    {"messages": [{"role": "user", "content": "¿Qué plan tengo?"}]},
    config=config,
)
```

`InMemorySaver` is for learning and tests; restarting the process loses it. In production, use a supported persistent checkpointer and apply encryption, authentication, backup, and retention. The
`thread_id` must belong to the authenticated user: accepting one arbitrarily from the client is a
horizontal access vulnerability.

## 4. Sliding window, summary, and selection

When the history grows, there are three complementary strategies:

1. **Window:** keeps system + last N turns. Cheap, but forgets old agreements.
2. **Cumulative summary:** compresses stable decisions and facts. Can introduce drift.
3. **Relevance-based selection:** retrieves memories related to the current turn.

Do not summarize everything into a single narrative paragraph. Use a verifiable schema:

```json
{
  "goal": "migrar alertas de NebulaOps",
  "decisions": [
    {"id": "d-17", "decision": "mantener PagerDuty", "source_turn": 12}
  ],
  "open_questions": ["ventana de mantenimiento"],
  "user_preferences": [
    {"key": "language", "value": "es", "confidence": 1.0, "source_turn": 1}
  ]
}
```

Keep pointers to the source turn to audit the summary. Regenerate it from the source when
you change the schema or the summary model.

## 5. Episodic memory

Record relevant events, not entire transcripts:

```json
{
  "memory_id": "mem-8f2c",
  "subject_id": "user-42",
  "kind": "decision",
  "content": "Prefiere despliegues los martes antes de las 12:00 Europe/Madrid",
  "source": {"thread_id": "conv-7", "turn": 18},
  "created_at": "2026-08-21T10:14:00Z",
  "expires_at": "2027-02-21T00:00:00Z",
  "confidence": 0.93,
  "status": "active"
}
```

A write policy should answer:

- Is it useful outside this conversation?
- Is it stable or just a fleeting preference?
- Was it stated by the user or inferred by the model?
- Is it sensitive and do we have grounds to retain it?
- When does it expire and how is it corrected or deleted?

Inferred memories must be marked as such and have lower confidence. Do not turn an ambiguous phrase into a permanent profile.

## 6. Semantic memory

Embed memories and retrieve top-k by similarity, always within the authorized namespace:

```text
namespace = (tenant_id, user_id, "preferences")
query = embedding(turno_actual)
candidate_memories = vector_search(namespace, query, top_k=8)
selected = rerank_and_filter(candidate_memories, min_score, not_expired=True)
```

Similarity alone is not enough. Combine:

- tenant/user scope;
- memory type;
- validity period;
- importance;
- confidence and provenance;
- diversity to avoid eight duplicates;
- token limit.

A retrieved memory is untrusted data: it may have been injected by a user or be obsolete.
It must not elevate its priority above the system prompt nor authorize actions.

## 7. Explicit vs. automatic writing

Three policies:

- **Explicit:** only "remember that...". Maximum control, lower convenience.
- **Automatic with schema:** an extractor proposes memories and deterministic rules filter them.
- **Automatic with confirmation:** the agent asks before saving sensitive or persistent data.

A good UX enables "What do you remember about me?", editing, and forgetting. Without these operations, memory is opaque and difficult to correct.

## 8. Security and privacy

Main risks:

- namespace mixing and leakage between users;
- indefinite retention of PII;
- persistent prompt injection stored as a memory;
- false memories that alter future decisions;
- unauthorized secondary use;
- backups that prevent compliance with deletion requests.

Controls:

1. authorization on every read/write, not just at login;
2. minimization and allowlist of saveable types;
3. encryption, TTL, and propagated deletion;
4. provenance, trust, and versioning;
5. content validation before injection;
6. access and change auditing;
7. separate tools for reading, writing, and deleting.

Never save keys, passwords, tokens, full payment data, or instructions that elevate privileges.

## 9. Evaluating memory

Do not measure "seems to remember". Create multi-turn sequences with ground truth:

- retention of a fact after 5, 20, and 50 turns;
- update: the user changes a preference;
- contradiction: two memories with different dates;
- isolation: another user asks about that data;
- forgetting: the user deletes a memory;
- irrelevance: the data exists but should not enter this turn;
- persistent injection: a message attempts to be saved as an instruction.

Metrics: recall of relevant memories, precision of injected memories, rate of obsolete data, isolation violations, context cost, and task success.

## 10. When you don't need memory

- the task ends in a single request;
- the data can be authoritatively queried from a DB;
- the user does not expect personalization;
- the risk of retaining outweighs the benefit;
- an explicit session identifier and state resolve the case.

Querying `get_customer_profile()` is better than "remembering" the billing plan: the DB is the
source of truth and updates without reconstructing memory.

## Common Errors

1. Forwarding the entire chat until context is exhausted.
2. Confusing checkpoints with semantic memory.
3. Saving inferences as confirmed facts.
4. Retrieving globally without a tenant namespace.
5. Failing to invalidate memories when the source of truth changes.
6. Evaluating only happy three-turn conversations.
7. Adding memory to solve a deterministic state problem.

## For Further Reading

- LangGraph, memory: https://docs.langchain.com/oss/python/langgraph/add-memory
- LangGraph, persistence: https://docs.langchain.com/oss/python/langgraph/persistence
- MemGPT: https://arxiv.org/abs/2310.08560
