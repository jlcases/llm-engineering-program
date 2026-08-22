# 04 — Advanced tool use: tool design, error handling, idempotency

> **Objective:** design tools that a model can use effectively: clear contracts, errors that
> teach, idempotency on retries. This file is transversal: it applies to labs 01–07 and
> the mini-project.

## 1. The thesis: an agent is only as good as its tools

When an agent fails, the instinct is to tweak the prompt. Experience (and Anthropic's engineering guide, *Writing tools for agents*) indicates that the major lever usually lies in the tools:
their names, descriptions, parameters, and what they return. The model does not see your code — it sees
exactly three things for each tool:

1. The **name**.
2. The **description** (docstring/description of the schema).
3. The **parameter JSON Schema** (names, types, descriptions, required fields).

And then, what the tool **returns**. These four surfaces are your only interface with
the model. Designing them well is writing documentation for a very literal reader, with limited
memory and no ability to ask your team questions.

## 2. Contract design

### 2.1 Names and granularity

- Verb + object, unambiguous: `search_flights`, `get_invoice`, `cancel_order`. Nothing like
   `helper`, `process`, `do_task`.
- **Few tools, well-separated.** If two tools overlap (`search` vs `find` vs
   `lookup`), the model alternates between them randomly. Merge them or differentiate them clearly in the
  description ("use X for...; for Y use tool Z").
- Granularity at the level of the **intent**, not the underlying API. Prefer
   `schedule_meeting(attendees, when)` over exposing `list_calendars` + `get_free_slots` +
   `create_event` and expecting the model to orchestrate three calls without errors. Consolidating frequent
  flows into one tool saves loop turns, tokens, and failures.

### 2.2 Descriptions

The description must answer: **what it does, when to use it, when NOT to use it, and what it returns.**

```python
@tool
def search_kb(query: str, max_results: int = 5) -> str:
    """Busca en la base de conocimiento interna de la empresa.

    Úsala para preguntas sobre políticas, procesos o documentación interna.
    NO la uses para información pública o actualidad (para eso usa web_search).
    Devuelve hasta max_results fragmentos con título y URL. Si no hay
    resultados, devuelve una lista vacía: reformula con sinónimos antes de rendirte.
    """
```

Treat descriptions as prompts: iterate on them with evaluations, not intuition.

### 2.3 Parameters

- Strict types and **enums** where the domain is closed (`status: Literal["open", "closed"]`)
   — each free string is an opportunity to hallucinate values.
- Self-explanatory names with units: `timeout_seconds`, not `t`. `amount_eur`, not `amount`.
- Few parameters with sensible defaults. A schema with 12 optional fields produces
  calls with absurd combinations.
- **Do not ask for what the system already knows.** If the `user_id` is in the session, inject it into the
  execution yourself; asking the model is inviting it to invent it (and a security hole: the model
  could pass another user's id).

### 2.4 What it returns (the forgotten surface)

The tool's response is the model's next prompt. Optimize it as such:

- **Return only what is necessary to solve the task**, not the raw API JSON with 40 fields. Each
  token in the observation is paid for in all remaining loops of the cycle.
- Model-readable format: structured text or compact JSON, ids only if actionable.
- Paginate/truncate with explicit signal: `"(mostrando 10 de 3.412 resultados — refina la búsqueda)"`
  is infinitely better than silent truncation, because it tells the model what to do next.

## 3. Error handling: errors are prompts

When a tool fails, the error text returns to the model. There are two schools:

- **Opaque error:** `"Error 500"` / 80-line traceback. The model blindly retries the same
   (→ loop) or gives up.
- **Instructive error:** a message that says what happened and **what to do differently**.

```python
def get_invoice(invoice_id: str) -> str:
    if not re.fullmatch(r"INV-\d{6}", invoice_id):
        return ("ERROR: formato de invoice_id inválido. Debe ser 'INV-' seguido de "
                "6 dígitos, p. ej. 'INV-004213'. Si no conoces el id, usa "
                "search_invoices(customer_name=...) primero.")
    return f"Factura {invoice_id}: estado=pendiente; total=129,00 EUR"
```

Rules:

1. **Catch all exceptions within the tool** and return them as structured error results. An uncaught exception kills the entire loop due to a single failure.
2. Distinguish **recoverable errors** ("reformulate", "missing parameter", "not found — try X")
   from **irrecoverable errors** ("service down") — and for irrecoverable ones, have the agent report and
   stop, not retry 10 times (remember the brakes from file 02).
3. Retries with backoff for transient network errors go **in your code**, not
   delegated to the model: they are deterministic and do not waste tokens.
4. Validate arguments **before** touching the real world. The model will hallucinate ids, impossible dates,
   and invented paths; your tool is the last line of defense.

## 4. Idempotency: Designing for Retry

Agents **retry**. Due to network timeouts (the operation arrived but the response was lost),
because the model repeats a tool call, or because you resumed from a checkpoint prior to
the result. If your tools mutate state, the question is not *if* they will execute twice, but
*what happens when it occurs*.

An operation is **idempotent** if executing it N times has the same effect as once:

| Operation | Idempotent? |
|---|---|
| `get_*` (reads) | Yes, by nature |
| `set_status(order, "shipped")` (absolute assignment) | Yes |
| `add_credit(user, 10)` (relative mutation) | **No** — double execution = double credit |
| `create_ticket(title)` | **No** — duplicates tickets |
| `delete_by_id(id)` | Almost — second time returns "does not exist" (must be treated as success) |

Techniques to achieve it:

- **Idempotency keys:** the tool accepts (or derives from arguments) a
   `idempotency_key`; the backend logs executed keys and on repetition returns the
  original result without re-executing. This is the pattern of Stripe's payment API, and applies identically
  to agent tools.
- **Prefer absolute assignments over relative mutations** (`set_quantity(5)` is better than
   `increment_quantity(1)`).
- **Upserts** instead of blind creates (`create_or_update_note(titulo, ...)`).
- **Treat "already done" as success**, not as an error: if `cancel_order` finds the order
  already cancelled, respond "the order was already cancelled" — informative and ends the loop, rather
  than an error that triggers more retries.

And for what cannot be idempotent or reversible (sending an email, executing a new payment):
**human-in-the-loop** (file 02, lab 04) or at least a dry-run mode by default.

## 5. Tool Execution Security

- **Least privilege:** the tool for "reading project files" does not need access to `/`. The
  SQL tool, a read-only user. Think of each tool as a public endpoint.
- **Code sandbox:** if the agent executes code or shell, do so in a container/subprocess
  with limits (time, memory, network). Never `eval()` on model strings in your process —
  in lab 01 the "calculator" uses a restricted AST evaluator exactly for this reason.
- **Allowlists over blocklists:** enumerating what is allowed (domains, tables, directories) is
  robust; enumerating what is prohibited always falls short.
- **Tool output is untrusted input** (prompt injection via content — seen in
  file 03 §5). Do not concatenate tool outputs into system prompts.

## 6. Design Checklist (for the mini-project)

Before considering a tool complete:

- [ ] Verb+object name; no overlap with other tools in the set.
- [ ] Description: what / when / when not / what it returns.
- [ ] Typed parameters, enums in closed domains, no data the system already knows.
- [ ] Minimal sufficient output; truncation with signal; no raw JSON of 40 fields.
- [ ] All exceptions caught; instructive errors that say what to do differently.
- [ ] Network retries in code, not delegated to the model.
- [ ] Idempotent mutations (or with idempotency key); "already done" = success.
- [ ] Irreversible actions: human approval or dry-run.
- [ ] Tested in isolation with malformed arguments (the ones the model will generate).

## For further reading

- Anthropic, *Writing tools for agents* (2025) — [anthropic.com/engineering/writing-tools-for-agents](https://www.anthropic.com/engineering/writing-tools-for-agents) — the central reference for this file.
- Anthropic, *Building effective agents* (2024) — appendix "Prompt engineering your tools".
- Anthropic's tool use docs — [docs.anthropic.com/en/docs/build-with-claude/tool-use](https://docs.anthropic.com/en/docs/build-with-claude/tool-use) — and OpenAI's function calling docs: [platform.openai.com/docs/guides/function-calling](https://platform.openai.com/docs/guides/function-calling)
- Stripe, *Idempotent requests* — [docs.stripe.com/api/idempotent_requests](https://docs.stripe.com/api/idempotent_requests) — the idempotency key pattern, directly transferable.
