# 03 — Function calling / tool use in OpenAI and Anthropic

> Associated Labs: [`../labs/03_function_calling_openai.py`](../labs/03_function_calling_openai.py) and [`../labs/04_tool_use_anthropic.py`](../labs/04_tool_use_anthropic.py)

## What it is (and what it isn't)

Function calling (OpenAI) or tool use (Anthropic) is the mechanism by which an LLM, instead of responding with text, **emits a structured request to invoke a function that you have described**, with JSON arguments that adhere to a schema.

What must be crystal clear from the very beginning:

> **The model never executes anything.** The model only generates a JSON that says "call `get_weather` with `{"city": "Valencia"}`". Executing the function is the responsibility of **your code**, which then returns the result to the model in a new message so it can continue.

This turns the LLM into a *planner/router* and your code into the *executor*. It is the foundational piece of agents (module 4): an agent is, essentially, a tool use loop with state.

## The complete loop

The flow is conceptually identical in both APIs:

```
1. Envías: mensajes + definiciones de herramientas (nombre, descripción, JSON Schema)
2. El modelo responde: o texto final, o una petición de tool call
3. Tu código ejecuta la función con los argumentos recibidos
4. Devuelves el resultado como mensaje del rol adecuado
5. Vuelves al paso 2 (el modelo puede pedir más herramientas o terminar)
```

The loop ends when the model responds with text without requesting tools (or when your code cuts off due to an iteration limit — make sure you set **this**; a confused model may request tools indefinitely).

## Function calling in OpenAI

The recommended API for new integrations is the **Responses API**. In it, the function definition is flat and the loop preserves the typed items returned by the model:

```python
tools = [{
    "type": "function",
    "name": "get_invoice",
    "description": (
        "Recupera una factura por su número. Úsala cuando el usuario "
        "pregunte por el estado, importe o detalle de una factura concreta."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "invoice_number": {
                "type": "string",
                "description": "Número de factura, formato FAC-YYYY-NNNN",
            },
        },
        "required": ["invoice_number"],
        "additionalProperties": False,
    },
    "strict": True,
}]

response = client.responses.create(
    model="gpt-5.6-luna",
    input=[{"role": "user", "content": "Consulta FAC-2026-0042"}],
    tools=tools,
)
```

The request appears as item `type == "function_call"` in `response.output`. It carries `call_id`,
`name` and `arguments` (a **JSON string**). All `response.output` is preserved and an item
`function_call_output` is added with the same `call_id`:

```python
input_items = [{"role": "user", "content": "Consulta FAC-2026-0042"}]
input_items.extend(response.output)

for item in response.output:
    if item.type != "function_call":
        continue
    args = json.loads(item.arguments)
    result = execute_tool(item.name, args)
    input_items.append({
        "type": "function_call_output",
        "call_id": item.call_id,
        "output": json.dumps(result),
    })

response = client.responses.create(
    model="gpt-5.6-luna",
    input=input_items,
    tools=tools,
)
print(response.output_text)
```

Control parameters: `tool_choice="auto"` (default), `"none"`, `"required"`, or a specific tool. With `strict: True`, OpenAI restricts arguments to the compatible schema; it still validates semantic rules in your code.

Chat Completions still appears in much code: there the definition lives under `function`, calls are in `message.tool_calls` and the result uses a `role="tool"` message. The lab teaches
Responses and comments on the equivalence so you can maintain both formats without mixing them.

## Tool use in Anthropic

Equivalent definition (note: the schema is called `input_schema` and there is no `function` wrapper):

```python
tools = [{
    "name": "get_invoice",
    "description": (
        "Recupera una factura por su número. Úsala cuando el usuario "
        "pregunte por el estado, importe o detalle de una factura concreta."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "invoice_number": {
                "type": "string",
                "description": "Número de factura, formato FAC-YYYY-NNNN",
            },
        },
        "required": ["invoice_number"],
    },
}]

response = client.messages.create(
    model="claude-haiku-4-5",
    max_tokens=1024,
    tools=tools,
    messages=messages,
)
```

Structural differences with OpenAI:

1. The request arrives as a **content block** `tool_use` inside `response.content` (which is a list of blocks: there can be a `text` block for "thinking out loud" *and* one or more `tool_use`), and `response.stop_reason == "tool_use"`.
2. The arguments (`block.input`) already come as a parsed **dict**, not as a string.
3. The result is returned as a `tool_result` block inside a **role `user`** message (there is no `tool` role):

```python
if response.stop_reason == "tool_use":
    messages.append({"role": "assistant", "content": response.content})
    results = []
    for block in response.content:
        if block.type == "tool_use":
            output = execute_tool(block.name, block.input)
            results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": json.dumps(output),
            })
    messages.append({"role": "user", "content": results})
    # ... nueva llamada a client.messages.create con messages ampliado
```

Control with `tool_choice`: `{"type": "auto"}`, `{"type": "any"}` (at least one required), `{"type": "tool", "name": "..."}` (a specific one). For strict argument validation, recent versions of the API accept `strict: true` in the tool definition (with the same closed schema requirements).

### Summary table of equivalences

| Concept | OpenAI | Anthropic |
|---|---|---|
| Parameter schema | `function.parameters` | `input_schema` |
| Tool call signal | items `function_call` in `response.output` | `stop_reason == "tool_use"` + blocks |
| Arguments | JSON string (`json.loads`) | already parsed dict |
| Result | item `function_call_output` + `call_id` | `role: "user"` + block `tool_result` + `tool_use_id` |
| Force tool | `tool_choice` of function | `tool_choice={"type":"tool",...}` |
| Parallel calls | multiple items `function_call` | multiple blocks `tool_use` in one message |

**Parallel calls**: both models can request multiple tools in the same turn. Important rule in Anthropic: it returns **all** the `tool_result` of the turn in **a single** message
`user`. In Responses, add one item `function_call_output` per `call_id` before proceeding.

**Tool errors**: do not swallow them or break the loop. Return the error as the result (`is_error: true` in the Anthropic block `tool_result`; a JSON `{"error": "..."}` in OpenAI) and let the model decide: retry with other arguments, use another tool, or explain it to the user.

## Designing good tools (where you win or lose)

The quality of tool use depends much more on the **descriptions** than on the loop code. The description is a mini-prompt: the model decides with it when to call and with what.

❌ **Bad definition:**

```json
{"name": "search", "description": "busca cosas",
 "parameters": {"q": {"type": "string"}}}
```

✅ **Good definition:**

```json
{
  "name": "search_knowledge_base",
  "description": "Busca en la base de conocimiento interna de soporte. Úsala para preguntas sobre funcionalidades del producto, precios o procedimientos. NO la uses para datos de clientes concretos (para eso, get_customer). Devuelve los 3 artículos más relevantes.",
  "parameters": {
    "query": {
      "type": "string",
      "description": "Consulta en lenguaje natural, en español. Ej.: 'cómo cambiar el IBAN de cobro'"
    }
  }
}
```

Principles (Anthropic and OpenAI guidelines coincide):

1. **Description = contract**: what it does, when to use it, when NOT to, what it returns. Anthropic recommends detailed descriptions (3–4+ sentences) as the factor that most improves performance.
2. **Explicit names** (`search_knowledge_base` > `search`), and if there are similar tools, descriptions should trace the boundary between them.
3. **Describe each parameter** with format and example. Argument failures are almost always due to under-described parameters.
4. **Few well-separated tools** > many overlapping ones. If two tools compete for the same cases, the model will alternate between them unstably.
5. **Enums and closed types** where the domain allows: `"enum": ["draft", "sent", "paid"]` prevents the model from inventing states.
6. **Always validate in your code** even when using `strict`: the schema guarantees form, not semantics (a well-formed date can still be absurd).

## When to use function calling and when not to

**Use it for:**

- Connect the model to fresh or private data (DBs, internal APIs) — the "tool RAG" pattern.
- Actions with effects (create ticket, send email) — with human confirmation for irreversible ones.
- Structured routing: "decide which of these 5 flows applies" by defining each flow as a tool.

**Do not use it for:**

- **Pure data extraction** when there is no actual function to execute: for that, use structured outputs (topic 04), which are simpler and more direct. (Historically, function calling was overused for this because it was the only way to guarantee JSON; it is no longer the case.)
- Calculations that your code can decide without the model: if the routing is deterministic (`if "factura" in texto`), do not pay for an LLM.
- Flows with complex orchestration of dozens of tools and steps: that is agent design (module 4), with its own planning and memory patterns.

## Common errors

1. **Forgetting to re-send the assistant's turn** (the one containing the tool calls) before the result — both APIs need the complete request/result pair in the history; if missing, error or erratic behavior occurs.
2. **Loop without iteration limit** — set a `max_iterations` (5–10) and log when it is reached.
3. **`json.loads` without error handling in OpenAI** — without `strict`, arguments may arrive
   malformed; catch and return a controlled error result.
4. **Descriptions that lie** — if the tool returns 3 results, do not say "returns all". The model reasons about what you tell it, not about your code.
5. **Injecting the result as free text in the next user prompt** instead of the correct role message — breaks the format the model expects and degrades future calls.
6. **"Do anything" tool** (a single generic `execute(sql)`) — the more open the tool, the larger the error surface and risk. Narrow, typed tools.

## To go deeper

- OpenAI — *Function calling guide*: https://platform.openai.com/docs/guides/function-calling
- Anthropic — *Tool use overview*: https://docs.anthropic.com/en/docs/build-with-claude/tool-use/overview
- Anthropic — *Implement tool use* (full loop and best practices): https://docs.anthropic.com/en/docs/build-with-claude/tool-use/implement-tool-use
- Anthropic — *Writing effective tool descriptions* (within the tool use guide).
- Schick, T. et al. (2023). *Toolformer: Language Models Can Teach Themselves to Use Tools*. arXiv:2302.04761.
- Yao, S. et al. (2022). *ReAct: Synergizing Reasoning and Acting in Language Models*. arXiv:2210.03629 — the conceptual bridge to the agents in module 4.
