# 04 — Structured outputs: JSON mode, response_format, Pydantic e Instructor

> Lab asociado: [`../labs/05_structured_outputs_instructor.py`](../labs/05_structured_outputs_instructor.py)

## El problema

Casi todo uso serio de un LLM en producción acaba en código que **parsea la salida**. Y el texto libre es un contrato pésimo: un día el modelo envuelve el JSON en ```` ```json ````, otro día añade "¡Claro! Aquí tienes:", otro emite una coma colgante. Cada uno de esos casos es un `JSONDecodeError` a las 3 de la mañana.

La evolución de las soluciones, de más frágil a más robusta:

```
1. "Responde en JSON, por favor"        → esperanza y regex
2. JSON mode                            → JSON sintácticamente válido, esquema no garantizado
3. Structured outputs (JSON Schema)     → JSON que cumple TU esquema (decodificación restringida)
4. Pydantic + Instructor                → esquema + validación semántica + reintentos, multi-proveedor
```

## Nivel 1: pedirlo por las buenas

Sigue siendo necesario aunque uses niveles superiores — describir el formato mejora el *contenido* de los campos:

```text
Extrae los datos del ticket y responde SOLO con un objeto JSON con las
claves: "categoria" (una de: facturacion|tecnico|cuenta|ventas),
"prioridad" (1-3), "resumen" (máx. 15 palabras).
Sin texto adicional antes ni después del JSON.
```

Pero por sí solo no da garantías. No construyas parsing de producción sobre esto.

## Nivel 2: JSON mode

En OpenAI: `response_format={"type": "json_object"}`. Garantiza que la salida es JSON **sintácticamente válido**... y nada más:

- No garantiza tus claves, ni los tipos, ni los enums.
- Exige que la palabra "JSON" aparezca en algún mensaje (si no, error de API).
- El modelo aún decide el esquema: puede devolverte `{"respuesta": "..."}` cuando esperabas `{"categoria": "..."}`.

JSON mode es un peldaño histórico: hoy solo tiene sentido cuando no puedes definir esquema (salida de forma genuinamente variable). Para todo lo demás, nivel 3.

## Nivel 3: Structured outputs con JSON Schema

OpenAI (agosto 2024 en adelante) implementa **decodificación restringida** (constrained decoding): la API compila tu JSON Schema a una gramática y **enmascara los tokens** que la violarían durante la generación. El resultado *no puede* salirse del esquema.

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

En Responses API, el SDK de Python ofrece `client.responses.parse(...,
text_format=MiModeloPydantic)`: convierte Pydantic a esquema y devuelve la instancia en
`response.output_parsed`. La forma raw equivalente se pasa con `text=text_config`. En Chat
Completions legado encontrarás `chat.completions.parse(..., response_format=MiModeloPydantic)`.

Restricciones del modo `strict` de OpenAI que hay que conocer: todos los campos deben estar en `required` (los opcionales se modelan como `"type": ["string", "null"]`), `additionalProperties: false` obligatorio, y hay subconjuntos de JSON Schema no soportados (p. ej. `minimum`/`maximum` no se aplican en la restricción — esa validación queda para tu código o Pydantic).

En **Anthropic** el equivalente moderno es el parámetro de formato de salida estructurado (`output_config`/formato con JSON Schema en las versiones recientes de la API, con `client.messages.parse()` en el SDK); históricamente el patrón era usar **tool use como canal de extracción** (defines una herramienta cuyo `input_schema` es tu esquema y fuerzas su uso con `tool_choice`), que sigue funcionando y es lo que Instructor usa por debajo con Claude. La lección transferible: *cualquier API con tool use estricto puede dar salidas estructuradas*, aunque exista o no un `response_format` nativo.

**Lo que la gramática no puede garantizar: la semántica.** `{"prioridad": 3, "resumen": "..."}` puede validar perfectamente y ser un análisis erróneo del ticket. La decodificación restringida elimina los errores de *forma*; los de *contenido* se miden con evaluación (tema 05).

## Nivel 4: Pydantic como contrato

Pydantic aporta lo que JSON Schema a pelo no da: tipos Python nativos, validadores semánticos y un único objeto que sirve de **contrato compartido** entre el prompt, la API y el resto de tu aplicación.

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

Detalles que importan más de lo que parece:

- **Los `description` de los `Field` llegan al modelo** (van dentro del esquema): son micro-prompts. Escríbelos con el mismo cuidado que el prompt principal.
- **El docstring de la clase también viaja** en muchas integraciones. Úsalo.
- Enums > strings libres, `ge`/`le` > "del 1 al 3" en prosa.

## Instructor: el pegamento

[Instructor](https://python.useinstructor.com/) parchea el cliente de OpenAI o Anthropic para aceptar `response_model=` con un modelo Pydantic, y cierra el ciclo completo:

> **Compatibilidad a 21-08-2026:** Instructor 1.15.4 declara OpenAI SDK `<3` y Rich
> `<15`, mientras el entorno principal del curso usa OpenAI 3.x y Rich 15. Ejecuta esta
> variante con `setup/requirements-instructor.txt`, como explica `setup/README.md`; el
> recorrido recomendado para OpenAI actual es `responses.parse`.

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

Qué hace por ti:

1. Convierte el modelo Pydantic al mecanismo nativo del proveedor (structured outputs en OpenAI, tool use en Anthropic — mismo código para ambos).
2. Parsea y **valida** la respuesta contra el modelo, validadores semánticos incluidos.
3. Si la validación falla, **reintenta automáticamente** (`max_retries`) reenviando al modelo el error de validación como feedback — el modelo corrige en el segundo intento en la gran mayoría de los casos.
4. Con `instructor.from_anthropic(Anthropic())` el mismo código funciona contra Claude.

Ese punto 3 es la diferencia cualitativa: la decodificación restringida garantiza forma; **los validadores Pydantic + retry garantizan también reglas de negocio** ("la fecha de fin debe ser posterior al inicio") con el modelo corrigiéndose a sí mismo.

### Patrones útiles con Instructor

**Extracción de listas** (N entidades de un texto):

```python
class Persona(BaseModel):
    nombre: str
    cargo: str | None

class Personas(BaseModel):
    personas: list[Persona]
```

**Campos con incertidumbre explícita** — pide la evidencia y permite el "no está":

```python
class DatoExtraido(BaseModel):
    valor: str | None = Field(description="null si el dato no aparece en el texto")
    cita_textual: str | None = Field(
        description="Fragmento literal del texto del que sale el valor"
    )
```

Pedir la cita literal junto al valor es una de las mitigaciones anti-alucinación más baratas que existen (tema 07): obliga al modelo a anclar cada dato y te da un campo verificable con `in texto`.

**Clasificación con evidencia breve** — pide una justificación verificable, no el razonamiento
interno completo. Colocarla antes de la etiqueta puede condicionar la decisión y facilita auditoría:

```python
class Clasificacion(BaseModel):
    evidencia: str = Field(description="Dato breve del texto que sustenta la categoría")
    categoria: Categoria
```

## Cuándo usar cada nivel

| Situación | Herramienta |
|---|---|
| Prototipo rápido, humano lee la salida | Instrucción de formato en el prompt |
| Salida de estructura libre pero JSON | JSON mode |
| Esquema fijo, un proveedor, sin validación de negocio | JSON Schema / `.parse()` nativo |
| Esquema + validación semántica + retries + multi-proveedor | Pydantic + Instructor |
| Extracción como parte de un flujo con herramientas reales | Function calling (tema 03) |

**Cuándo NO usar salidas estructuradas:** en tareas genuinamente generativas (redacción, resumen
para humanos). Forzar un esquema restringe la fluidez y no aporta nada si nadie parsea el
resultado. En tareas complejas, separa resolución y estructuración cuando tu evaluación demuestre
que una sola pasada degrada calidad; conserva evidencia verificable en vez de solicitar un
chain-of-thought privado.

## Errores comunes

1. **Reinventar Instructor a mano** con regex + `json.loads` + bucles de retry artesanales. Ya está resuelto y testeado.
2. **Esquemas gigantes de 40 campos en una llamada**: la calidad por campo cae. Divide en varias extracciones o usa dos pasadas.
3. **`Optional` sin instrucción**: si un campo puede faltar, dilo en el `description` ("null si no aparece"); si no, el modelo tenderá a **inventar** el valor antes que omitirlo.
4. **Olvidar que los `description` son prompt**: campos sin describir = modelo adivinando semántica ("¿`fecha` es la de emisión o la de vencimiento?").
5. **Validar solo la forma y no medir el contenido**: 100% de JSON válido no es 100% de extracción correcta. El dataset de test del tema 05 aplica igual aquí.
6. **Usar `float` para dinero** en el modelo Pydantic. `Decimal` (o céntimos como `int`). Esto no es de LLMs, pero se ve cada semana.

## Para profundizar

- OpenAI — *Structured Outputs guide*: https://developers.openai.com/api/docs/guides/structured-outputs
- Anthropic — *Structured outputs*: https://docs.anthropic.com/en/docs/build-with-claude/structured-outputs
- Documentación de Instructor: https://python.useinstructor.com/
- Documentación de Pydantic v2: https://docs.pydantic.dev/latest/
- Willard, B. & Louf, R. (2023). *Efficient Guided Generation for Large Language Models* (base teórica de la decodificación restringida, lib Outlines). arXiv:2307.09702.
- Tam, Z. R. et al. (2024). *Let Me Speak Freely? A Study on the Impact of Format Restrictions on Performance of Large Language Models*. arXiv:2408.02442.
