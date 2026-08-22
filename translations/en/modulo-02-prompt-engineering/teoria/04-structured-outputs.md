# 04 — Structured outputs: JSON mode, response_format, Pydantic and Instructor

> Associated lab: [`../labs/05_structured_outputs_instructor.py`](../labs/05_structured_outputs_instructor.py)

## The problem

Almost any serious production use of an LLM ends up with code that **parses the output**. Free-form text is a flawed contract: one day the model wraps the JSON in ```` ```json ````, another day it adds "Sure! Here you go:", another emits a trailing comma. Each of these cases is a `JSONDecodeError` at 3 AM.

The evolution of solutions, from most fragile to most robust:

```
1. "Responde en JSON, por favor"        → esperanza y regex
2. JSON mode                            → JSON sintácticamente válido, esquema no garantizado
3. Structured outputs (JSON Schema)     → JSON que cumple TU esquema (decodificación restringida)
4. Pydantic + Instructor                → esquema + validación semántica + reintentos, multi-proveedor
```

## Level 1: asking politely

It remains necessary even when you use higher levels — describing the format improves the *content* of the fields:

```text
Extrae los datos del ticket y responde SOLO con un objeto JSON con las
claves: "categoria" (una de: facturacion|tecnico|cuenta|ventas),
"prioridad" (1-3), "resumen" (máx. 15 palabras).
Sin texto adicional antes ni después del JSON.
```

But on its own it provides no guarantees. Do not build production-grade parsing on top of this.

## Level 2: JSON mode

In OpenAI: `response_format={"type": "json_object"}`. It guarantees that the output is **syntactically valid** JSON... and nothing more:

- It does not guarantee your keys, types, or enums.
- It requires the word "JSON" to appear in the response (otherwise, an API error occurs).
- The model still determines the schema: it may return `{"respuesta": "..."}` when you expected `{"categoria": "..."}`.

JSON mode is a historical stepping stone: today it only makes sense when you cannot define a schema (for genuinely variable output formats). For everything else, use level 3.

## Level 3: Structured outputs with JSON Schema

OpenAI (from August 2024 onward) implements **constrained decoding**: the API compiles your JSON Schema into a grammar and **masks tokens** that would violate it during generation. The output *cannot* deviate from the schema.

```python
text_config = {
    "format": {
        "type": "json_schema",
        "name": "ticket_analysis",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "categoria": {
                    "type": "string",
                    "enum": ["facturacion", "tecnico", "cuenta", "ventas"],
                },
                "prioridad": {"type": "integer"},
                "resumen": {"type": "string"},
            },
            "required": ["categoria", "prioridad", "resumen"],
            "additionalProperties": False,
        },
    },
}
```

In the Responses API, the Python SDK provides `client.responses.parse(...,
text_format=MiModeloPydantic)`: it converts Pydantic to a schema and returns the instance in
`response.output_parsed`. The equivalent raw form is passed via `text=text_config`. In legacy
Chat Completions you will encounter `chat.completions.parse(..., response_format=MiModeloPydantic)`.

Key constraints for OpenAI's `strict` mode: all fields must be present in `required` (optional fields are modeled as `"type": ["string", "null"]`), `additionalProperties: false` is required, and certain JSON Schema subsets are unsupported (e.g., `minimum`/`maximum` are not enforced by the constraint — that validation is left to your code or Pydantic).

For **Anthropic**, the modern equivalent is the structured output format parameter (`output_config`/format with JSON Schema in recent API versions, with `client.messages.parse()` in the SDK); historically, the pattern was to use **tool use as an extraction channel** (you define a tool whose `input_schema` is your schema and force its use with `tool_choice`), which still works and is what Instructor uses under the hood with Claude. The transferable lesson: *any API with strict tool use can produce structured outputs*, regardless of whether a native `response_format` exists.

**What the grammar cannot guarantee: semantics.** `{"prioridad": 3, "resumen": "..."}` can validate perfectly and still represent a misinterpretation of the ticket. Constrained decoding eliminates *format* errors; *content* errors are assessed via evaluation (topic 05).

## Level 4: Pydantic as a Contract

Pydantic provides what raw JSON Schema lacks: native Python types, semantic validators, and a single object that serves as a **shared contract** between the prompt, the API, and the rest of your application.

```python
from pydantic import BaseModel, Field, field_validator
from enum import Enum

class Categoria(str, Enum):
    FACTURACION = "facturacion"
    TECNICO = "tecnico"
    CUENTA = "cuenta"
    VENTAS = "ventas"

class TicketAnalysis(BaseModel):
    """Análisis estructurado de un ticket de soporte."""
    categoria: Categoria
    prioridad: int = Field(ge=1, le=3, description="1=baja, 2=media, 3=urgente")
    resumen: str = Field(max_length=120, description="Resumen en una frase, en español")

    @field_validator("resumen")
    @classmethod
    def resumen_no_vacio(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("el resumen no puede estar vacío")
        return v
```

Details that matter more than they seem:

- **The `description` of the `Field` reach the model** (they go inside the schema): they are micro-prompts. Write them with the same care as the main prompt.
- **The class docstring also gets passed along** in many integrations. Use it.
- Enums > free strings, `ge`/`le` > "from 1 to 3" in prose.

## Instructor: the glue

[Instructor](https://python.useinstructor.com/) patches the OpenAI or Anthropic client to accept `response_model=` with a Pydantic model, and completes the full loop:

> **Compatibility as of 21-08-2026:** Instructor 1.15.4 specifies OpenAI SDK `<3` and Rich
> `<15`, while the primary course environment uses OpenAI 3.x and Rich 15. Run this
> variant with `setup/requirements-instructor.txt`, as explained in `setup/README.md`; the
> recommended path for current OpenAI is `responses.parse`.

```python
import instructor
from openai import OpenAI

client = instructor.from_openai(OpenAI())

analysis = client.chat.completions.create(
    model="gpt-5.6-luna",
    response_model=TicketAnalysis,
    max_retries=2,
    messages=[
        {"role": "system", "content": "Analiza tickets de soporte de un SaaS de facturación."},
        {"role": "user", "content": f"<ticket>{ticket_text}</ticket>"},
    ],
)
# analysis es una instancia de TicketAnalysis, tipada y validada
```

What it does for you:

1. Converts the Pydantic model to the provider's native mechanism (structured outputs in OpenAI, tool use in Anthropic — same code for both).
2. Parses and **validates** the response against the model, including semantic validators.
3. If validation fails, **automatically retries** (`max_retries`) by sending the validation error back to the model as feedback — the model corrects itself on the second attempt in the vast majority of cases.
4. With `instructor.from_anthropic(Anthropic())` the same code runs against Claude.

Point 3 is the qualitative difference: constrained decoding guarantees format; **Pydantic validators + retry also enforce business rules** ("the end date must be after the start date") with the model correcting itself.

### Useful patterns with Instructor

**List extraction** (N entities from a text):

```python
class Persona(BaseModel):
    nombre: str
    cargo: str | None

class Personas(BaseModel):
    personas: list[Persona]
```

**Fields with explicit uncertainty** — request the evidence and allow "not present":

```python
class DatoExtraido(BaseModel):
    valor: str | None = Field(description="null si el dato no aparece en el texto")
    cita_textual: str | None = Field(
        description="Fragmento literal del texto del que sale el valor"
    )
```

Requesting the literal quote alongside the value is one of the most cost-effective anti-hallucination mitigations available (topic 07): it forces the model to anchor each data point and gives you a verifiable field with `in texto`.

**Classification with brief evidence** — request a verifiable justification, not the full
internal reasoning. Placing it before the label can influence the decision and facilitates auditing:

```python
class Clasificacion(BaseModel):
    evidencia: str = Field(description="Dato breve del texto que sustenta la categoría")
    categoria: Categoria
```

## When to use each level

| Situation | Tool |
|---|---|
| Quick prototype, human reads the output | Format instruction in the prompt |
| Free-form but JSON output | JSON mode |
| Fixed schema, single provider, no business validation | JSON Schema / native `.parse()` |
| Schema + semantic validation + retries + multi-provider | Pydantic + Instructor |
| Extraction as part of a flow with real tools | Function calling (topic 03) |

**When NOT to use structured outputs:** in genuinely generative tasks (drafting, summarizing
for humans). Forcing a schema restricts fluency and adds nothing if no one parses the
result. In complex tasks, separate resolution and structuring when your evaluation shows
that a single pass degrades quality; preserve verifiable evidence instead of requesting a
private chain-of-thought.

## Common mistakes

1. **Reinventing Instructor manually** with regex + `json.loads` + handcrafted retry loops. It is already solved and tested.
2. **Massive schemas with 40 fields in a single call**: quality per field drops. Split into multiple extractions or use two passes.
3. **`Optional` without instruction**: if a field can be missing, state it in the `description` ("null if not present"); otherwise, the model will tend to **invent** the value rather than omit it.
4. **Forgetting that `description` are prompt**: fields without descriptions = model guessing semantics ("Is `fecha` the issue date or the maturity date?").
5. **Validating only the shape and not measuring the content**: 100% valid JSON does not mean 100% correct extraction. The test dataset from topic 05 applies equally here.
6. **Using `float` for monetary values** in the Pydantic model. `Decimal` (or cents as `int`). This isn't LLM-specific, but it comes up every week.

## For further reading

- OpenAI — *Structured Outputs guide*: https://developers.openai.com/api/docs/guides/structured-outputs
- Anthropic — *Structured outputs*: https://docs.anthropic.com/en/docs/build-with-claude/structured-outputs
- Instructor documentation: https://python.useinstructor.com/
- Pydantic v2 documentation: https://docs.pydantic.dev/latest/
- Willard, B. & Louf, R. (2023). *Efficient Guided Generation for Large Language Models* (theoretical basis for constrained decoding, Outlines library). arXiv:2307.09702.
- Tam, Z. R. et al. (2024). *Let Me Speak Freely? A Study on the Impact of Format Restrictions on Performance of Large Language Models*. arXiv:2408.02442.
