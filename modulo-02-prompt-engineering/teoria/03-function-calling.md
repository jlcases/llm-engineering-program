# 03 — Function calling / tool use en OpenAI y Anthropic

> Labs asociados: [`../labs/03_function_calling_openai.py`](../labs/03_function_calling_openai.py) y [`../labs/04_tool_use_anthropic.py`](../labs/04_tool_use_anthropic.py)

## Qué es (y qué no es)

Function calling (OpenAI) o tool use (Anthropic) es el mecanismo por el que un LLM, en vez de responder con texto, **emite una petición estructurada de invocar una función que tú has descrito**, con argumentos en JSON que respetan un esquema.

Lo que hay que tener clarísimo desde el minuto uno:

> **El modelo nunca ejecuta nada.** El modelo solo genera un JSON que dice "llama a `get_weather` con `{"city": "Valencia"}`". Ejecutar la función es responsabilidad de **tu código**, que después devuelve el resultado al modelo en un nuevo mensaje para que continúe.

Esto convierte al LLM en un *planificador/enrutador* y a tu código en el *ejecutor*. Es la pieza fundacional de los agentes (módulo 4): un agente es, esencialmente, un bucle de tool use con estado.

## El bucle completo

El flujo es idéntico conceptualmente en ambas APIs:

```
1. Envías: mensajes + definiciones de herramientas (nombre, descripción, JSON Schema)
2. El modelo responde: o texto final, o una petición de tool call
3. Tu código ejecuta la función con los argumentos recibidos
4. Devuelves el resultado como mensaje del rol adecuado
5. Vuelves al paso 2 (el modelo puede pedir más herramientas o terminar)
```

El bucle termina cuando el modelo responde texto sin pedir herramientas (o cuando tu código corta por límite de iteraciones — ponlo **siempre**; un modelo confundido puede pedir herramientas indefinidamente).

## Function calling en OpenAI

La API recomendada para integraciones nuevas es **Responses API**. En ella la definición de la
función es plana y el bucle conserva los items tipados que devuelve el modelo:

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

La petición aparece como item `type == "function_call"` en `response.output`. Trae `call_id`,
`name` y `arguments` (un **string** JSON). Se conserva todo `response.output` y se añade un item
`function_call_output` con el mismo `call_id`:

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

Parámetros de control: `tool_choice="auto"` (por defecto), `"none"`, `"required"`, o una tool
concreta. Con `strict: True` OpenAI restringe los argumentos al esquema compatible; sigue validando
reglas semánticas en tu código.

Chat Completions sigue apareciendo en mucho código: allí la definición vive bajo `function`, las
llamadas están en `message.tool_calls` y el resultado usa un mensaje `role="tool"`. El lab enseña
Responses y comenta la equivalencia para que puedas mantener ambos formatos sin mezclarlos.

## Tool use en Anthropic

Definición equivalente (fíjate: el esquema se llama `input_schema` y no hay envoltorio `function`):

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

Diferencias estructurales con OpenAI:

1. La petición llega como **bloque de contenido** `tool_use` dentro de `response.content` (que es una lista de bloques: puede haber un bloque `text` de "pensamiento en voz alta" *y* uno o varios `tool_use`), y `response.stop_reason == "tool_use"`.
2. Los argumentos (`block.input`) ya vienen como **dict parseado**, no como string.
3. El resultado se devuelve como bloque `tool_result` dentro de un mensaje de **rol `user`** (no existe rol `tool`):

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

Control con `tool_choice`: `{"type": "auto"}`, `{"type": "any"}` (alguna obligatoria), `{"type": "tool", "name": "..."}` (una concreta). Para validación estricta de argumentos, las versiones recientes de la API aceptan `strict: true` en la definición de la herramienta (con los mismos requisitos de esquema cerrado).

### Tabla resumen de equivalencias

| Concepto | OpenAI | Anthropic |
|---|---|---|
| Esquema de parámetros | `function.parameters` | `input_schema` |
| Señal de tool call | items `function_call` en `response.output` | `stop_reason == "tool_use"` + bloques |
| Argumentos | string JSON (`json.loads`) | dict ya parseado |
| Resultado | item `function_call_output` + `call_id` | `role: "user"` + bloque `tool_result` + `tool_use_id` |
| Forzar herramienta | `tool_choice` de función | `tool_choice={"type":"tool",...}` |
| Llamadas paralelas | varios items `function_call` | varios bloques `tool_use` en un mensaje |

**Llamadas paralelas**: ambos modelos pueden pedir varias herramientas en el mismo turno. Regla
importante en Anthropic: devuelve **todos** los `tool_result` del turno en **un único** mensaje
`user`. En Responses, añade un item `function_call_output` por `call_id` antes de continuar.

**Errores de herramienta**: no los tragues ni rompas el bucle. Devuelve el error como resultado (`is_error: true` en el bloque `tool_result` de Anthropic; un JSON `{"error": "..."}` en OpenAI) y deja que el modelo decida: reintentar con otros argumentos, usar otra herramienta o explicárselo al usuario.

## Diseñar buenas herramientas (donde se gana o se pierde)

La calidad del tool use depende mucho más de las **descripciones** que del código del bucle. La descripción es un mini-prompt: el modelo decide con ella cuándo llamar y con qué.

❌ **Mala definición:**

```json
{"name": "search", "description": "busca cosas",
 "parameters": {"q": {"type": "string"}}}
```

✅ **Buena definición:**

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

Principios (coinciden las guías de Anthropic y OpenAI):

1. **Descripción = contrato**: qué hace, cuándo usarla, cuándo NO, qué devuelve. Anthropic recomienda descripciones detalladas (3–4+ frases) como el factor que más mejora el rendimiento.
2. **Nombres explícitos** (`search_knowledge_base` > `search`), y si hay herramientas parecidas, que las descripciones tracen la frontera entre ellas.
3. **Describe cada parámetro** con formato y ejemplo. Los fallos de argumentos casi siempre son parámetros infra-descritos.
4. **Pocas herramientas bien separadas** > muchas solapadas. Si dos herramientas compiten por los mismos casos, el modelo alternará entre ellas de forma inestable.
5. **Enums y tipos cerrados** donde el dominio lo permita: `"enum": ["draft", "sent", "paid"]` evita que el modelo invente estados.
6. **Valida siempre en tu código** aunque uses `strict`: el esquema garantiza forma, no semántica (una fecha bien formada puede ser absurda igualmente).

## Cuándo usar function calling y cuándo no

**Úsalo para:**

- Conectar el modelo con datos frescos o privados (BD, APIs internas) — el patrón "RAG de herramienta".
- Acciones con efectos (crear ticket, enviar email) — con confirmación humana para lo irreversible.
- Enrutado estructurado: "decide cuál de estos 5 flujos aplica" definiendo cada flujo como herramienta.

**No lo uses para:**

- **Extracción de datos pura** cuando no hay ninguna función real que ejecutar: para eso están los structured outputs (tema 04), más simples y directos. (Históricamente se abusó de function calling para esto porque era la única forma de garantizar JSON; ya no lo es.)
- Cálculos que tu código puede decidir sin el modelo: si el enrutado es determinista (`if "factura" in texto`), no pagues un LLM.
- Flujos con orquestación compleja de decenas de herramientas y pasos: eso ya es diseño de agentes (módulo 4), con sus patrones propios de planificación y memoria.

## Errores comunes

1. **Olvidar re-enviar el turno del asistente** (el que contiene los tool calls) antes del resultado — ambas APIs necesitan el par petición/resultado completo en el historial; si falta, error o comportamiento errático.
2. **Bucle sin límite de iteraciones** — pon un `max_iterations` (5–10) y registra cuándo se alcanza.
3. **`json.loads` sin manejo de error en OpenAI** — sin `strict`, los argumentos pueden llegar
   malformados; captura y devuelve un resultado de error controlado.
4. **Descripciones que mienten** — si la herramienta devuelve 3 resultados, no digas "devuelve todos". El modelo razona sobre lo que le dices, no sobre tu código.
5. **Inyectar el resultado como texto libre en el siguiente prompt de usuario** en lugar del mensaje de rol correcto — rompe el formato que el modelo espera y degrada llamadas futuras.
6. **Herramienta "haz cualquier cosa"** (un solo `execute(sql)` genérico) — cuanto más abierta la herramienta, más superficie de error y de riesgo. Herramientas estrechas y tipadas.

## Para profundizar

- OpenAI — *Function calling guide*: https://platform.openai.com/docs/guides/function-calling
- Anthropic — *Tool use overview*: https://docs.anthropic.com/en/docs/build-with-claude/tool-use/overview
- Anthropic — *Implement tool use* (bucle completo y mejores prácticas): https://docs.anthropic.com/en/docs/build-with-claude/tool-use/implement-tool-use
- Anthropic — *Writing effective tool descriptions* (dentro de la guía de tool use).
- Schick, T. et al. (2023). *Toolformer: Language Models Can Teach Themselves to Use Tools*. arXiv:2302.04761.
- Yao, S. et al. (2022). *ReAct: Synergizing Reasoning and Acting in Language Models*. arXiv:2210.03629 — el puente conceptual hacia los agentes del módulo 4.
