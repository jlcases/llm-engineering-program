# 04 — Tool use avanzado: diseño de herramientas, manejo de errores, idempotencia

> **Objetivo:** diseñar herramientas que un modelo pueda usar bien: contratos claros, errores que
> enseñan, idempotencia ante reintentos. Este fichero es transversal: aplica a los labs 01–07 y
> al mini-proyecto.

## 1. La tesis: el agente es tan bueno como sus herramientas

Cuando un agente falla, el instinto es tocar el prompt. La experiencia (y la guía de ingeniería de
Anthropic, *Writing tools for agents*) dice que la palanca grande suele estar en las herramientas:
sus nombres, descripciones, parámetros, y lo que devuelven. El modelo no ve tu código — ve
exactamente tres cosas de cada herramienta:

1. El **nombre**.
2. La **descripción** (docstring/description del schema).
3. El **JSON Schema de parámetros** (nombres, tipos, descripciones, requeridos).

Y después, lo que la herramienta **devuelve**. Esas cuatro superficies son tu única interfaz con
el modelo. Diseñarlas bien es escribir documentación para un lector muy literal, con memoria
limitada y sin capacidad de preguntar a tu equipo.

## 2. Diseño del contrato

### 2.1 Nombres y granularidad

- Verbo + objeto, sin ambigüedad: `search_flights`, `get_invoice`, `cancel_order`. Nada de
  `helper`, `process`, `do_task`.
- **Pocas herramientas, bien separadas.** Si dos tools se solapan (`search` vs `find` vs
  `lookup`), el modelo alterna entre ellas al azar. Fusiónalas o diferéncialas nítidamente en la
  descripción ("usa X para...; para Y usa la herramienta Z").
- Granularidad al nivel de la **intención**, no de la API subyacente. Mejor
  `schedule_meeting(attendees, when)` que exponer `list_calendars` + `get_free_slots` +
  `create_event` y esperar que el modelo orqueste tres llamadas sin errores. Consolidar flujos
  frecuentes en una tool ahorra vueltas de bucle, tokens y fallos.

### 2.2 Descripciones

La descripción debe responder: **qué hace, cuándo usarla, cuándo NO usarla, y qué devuelve.**

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

Trata las descripciones como prompts que son: itera sobre ellas con evaluaciones, no por intuición.

### 2.3 Parámetros

- Tipos estrictos y **enums** donde el dominio es cerrado (`status: Literal["open", "closed"]`)
  — cada string libre es una oportunidad de alucinar valores.
- Nombres autoexplicativos con unidades: `timeout_seconds`, no `t`. `amount_eur`, no `amount`.
- Pocos parámetros y con defaults sensatos. Un schema de 12 campos opcionales produce llamadas
  con combinaciones absurdas.
- **No pidas lo que el sistema ya sabe.** Si el `user_id` está en la sesión, inyéctalo tú en la
  ejecución; pedírselo al modelo es invitarle a inventárselo (y un agujero de seguridad: el modelo
  podría pasar el id de otro usuario).

### 2.4 Lo que devuelve (la superficie olvidada)

La respuesta de la herramienta es el siguiente prompt del modelo. Optimízala como tal:

- **Devuelve lo mínimo que resuelve la tarea**, no el JSON crudo de la API con 40 campos. Cada
  token de la observación se paga en todas las vueltas restantes del bucle.
- Formato legible por el modelo: texto estructurado o JSON compacto, ids solo si son accionables.
- Pagina/trunca con señal explícita: `"(mostrando 10 de 3.412 resultados — refina la búsqueda)"`
  es infinitamente mejor que truncar en silencio, porque le dice al modelo qué hacer después.

## 3. Manejo de errores: los errores son prompts

Cuando una herramienta falla, el texto del error vuelve al modelo. Hay dos escuelas:

- **Error opaco:** `"Error 500"` / traceback de 80 líneas. El modelo reintenta a ciegas lo mismo
  (→ loop) o abandona.
- **Error instructivo:** un mensaje que dice qué pasó y **qué hacer distinto**.

```python
def get_invoice(invoice_id: str) -> str:
    if not re.fullmatch(r"INV-\d{6}", invoice_id):
        return ("ERROR: formato de invoice_id inválido. Debe ser 'INV-' seguido de "
                "6 dígitos, p. ej. 'INV-004213'. Si no conoces el id, usa "
                "search_invoices(customer_name=...) primero.")
    return f"Factura {invoice_id}: estado=pendiente; total=129,00 EUR"
```

Reglas:

1. **Captura todas las excepciones dentro de la herramienta** y devuélvelas como resultado de
   error estructurado. Una excepción sin capturar mata el bucle entero por un fallo puntual.
2. Distingue **error recuperable** ("reformula", "falta parámetro", "no encontrado — prueba X")
   de **irrecuperable** ("servicio caído") — y para los irrecuperables, que el agente informe y
   pare, no que reintente 10 veces (recuerda los frenos del fichero 02).
3. Los reintentos con backoff ante errores transitorios de red van **en tu código**, no
   delegados al modelo: son deterministas y no gastan tokens.
4. Valida los argumentos **antes** de tocar el mundo real. El modelo alucinará ids, fechas
   imposibles y paths inventados; tu herramienta es la última línea de defensa.

## 4. Idempotencia: diseñar para el reintento

Los agentes **reintentan**. Por timeout de red (la operación llegó pero la respuesta se perdió),
porque el modelo repite un tool call, o porque reanudaste desde un checkpoint anterior al
resultado. Si tus herramientas mutan estado, la pregunta no es *si* se ejecutarán dos veces, sino
*qué pasa cuando ocurra*.

Una operación es **idempotente** si ejecutarla N veces tiene el mismo efecto que una:

| Operación | ¿Idempotente? |
|---|---|
| `get_*` (lecturas) | Sí, por naturaleza |
| `set_status(order, "shipped")` (asignación absoluta) | Sí |
| `add_credit(user, 10)` (mutación relativa) | **No** — doble ejecución = doble abono |
| `create_ticket(title)` | **No** — duplica tickets |
| `delete_by_id(id)` | Casi — segunda vez da "no existe" (debe tratarse como éxito) |

Técnicas para conseguirla:

- **Claves de idempotencia:** la herramienta acepta (o deriva de los argumentos) un
  `idempotency_key`; el backend registra las claves ejecutadas y ante una repetición devuelve el
  resultado original sin re-ejecutar. Es el patrón de la API de pagos de Stripe, y aplica idéntico
  a tools de agentes.
- **Preferir asignaciones absolutas a mutaciones relativas** (`set_quantity(5)` mejor que
  `increment_quantity(1)`).
- **Upserts** en lugar de create ciego (`create_or_update_note(titulo, ...)`).
- **Tratar "ya estaba hecho" como éxito**, no como error: si `cancel_order` encuentra el pedido
  ya cancelado, responde "el pedido ya estaba cancelado" — informativo y termina el bucle, en vez
  de un error que provoca más reintentos.

Y para lo que no puede ser idempotente ni reversible (enviar un email, ejecutar un pago nuevo):
**human-in-the-loop** (fichero 02, lab 04) o al menos un modo dry-run por defecto.

## 5. Seguridad en la ejecución de herramientas

- **Mínimo privilegio:** la tool de "leer ficheros del proyecto" no necesita acceso a `/`. La de
  SQL, un usuario de solo lectura. Piensa en cada tool como en un endpoint público.
- **Sandbox para código:** si el agente ejecuta código o shell, hazlo en contenedor/subproceso
  con límites (tiempo, memoria, red). Nunca `eval()` sobre strings del modelo en tu proceso —
  en el lab 01 la "calculadora" usa un evaluador AST restringido exactamente por esto.
- **Allowlists sobre blocklists:** enumerar lo permitido (dominios, tablas, directorios) es
  robusto; enumerar lo prohibido siempre se queda corto.
- **La salida de la tool es entrada no confiable** (prompt injection vía contenido — visto en el
  fichero 03 §5). No concatenes salidas de tools en prompts de sistema.

## 6. Checklist de diseño (para el mini-proyecto)

Antes de dar una herramienta por terminada:

- [ ] Nombre verbo+objeto; sin solaparse con otra tool del set.
- [ ] Descripción: qué / cuándo / cuándo no / qué devuelve.
- [ ] Parámetros tipados, enums en dominios cerrados, sin datos que el sistema ya conoce.
- [ ] Salida mínima suficiente; truncado con señal; sin JSON crudo de 40 campos.
- [ ] Toda excepción capturada; errores instructivos que dicen qué hacer distinto.
- [ ] Reintentos de red en código, no delegados al modelo.
- [ ] Mutaciones idempotentes (o con clave de idempotencia); "ya estaba hecho" = éxito.
- [ ] Acciones irreversibles: aprobación humana o dry-run.
- [ ] Probada en aislamiento con argumentos malformados (los que el modelo generará).

## Para profundizar

- Anthropic, *Writing tools for agents* (2025) — [anthropic.com/engineering/writing-tools-for-agents](https://www.anthropic.com/engineering/writing-tools-for-agents) — la referencia central de este fichero.
- Anthropic, *Building effective agents* (2024) — apéndice "Prompt engineering your tools".
- Docs de tool use de Anthropic — [docs.anthropic.com/en/docs/build-with-claude/tool-use](https://docs.anthropic.com/en/docs/build-with-claude/tool-use) — y las de function calling de OpenAI: [platform.openai.com/docs/guides/function-calling](https://platform.openai.com/docs/guides/function-calling)
- Stripe, *Idempotent requests* — [docs.stripe.com/api/idempotent_requests](https://docs.stripe.com/api/idempotent_requests) — el patrón de claves de idempotencia, transplantable tal cual.
