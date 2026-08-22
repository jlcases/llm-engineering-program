# 06 — Memoria de agentes: trabajo, episódica y semántica

> Lab asociado: [`../labs/07_memoria_agente.py`](../labs/07_memoria_agente.py)

La memoria de un agente no es una conversación infinita. Es una política para decidir **qué
conservar, dónde, durante cuánto tiempo y cuándo recuperarlo**. Guardar todo encarece cada turno,
mezcla datos irrelevantes y crea riesgos de privacidad; no guardar nada obliga al usuario a
repetirse. Diseñar memoria es diseñar selección y olvido.

## 1. Cuatro conceptos que suelen mezclarse

| Concepto | Vida | Ejemplo | Mecanismo |
|---|---|---|---|
| Estado de trabajo | un run | plan actual, resultados de tools | `State` del grafo |
| Historial del thread | una conversación | mensajes y checkpoints | checkpointer |
| Memoria episódica | entre conversaciones | "el usuario rechazó la opción X" | store persistente |
| Memoria semántica | entre conversaciones | preferencias/hechos recuperables | store + búsqueda |

El **context window** es solo el espacio que recibe el modelo en una llamada. Puede contener una
selección de las cuatro capas, pero no es por sí mismo una memoria.

## 2. Estado de trabajo

Contiene lo necesario para completar la tarea actual:

```python
from typing import TypedDict


class AgentState(TypedDict):
    messages: list
    plan: list[str]
    completed_steps: list[str]
    tool_errors: list[dict[str, str]]
    remaining_budget_cents: float
```

Haz explícitos límites y contadores. Si el número de iteraciones solo existe en una variable
local, desaparece al reanudar desde un checkpoint.

Evita meter en el estado objetos no serializables, clientes HTTP o conexiones de base de datos.
El estado es dato; las dependencias se inyectan al nodo.

## 3. Memoria corta con checkpoints

Un checkpointer de LangGraph guarda snapshots por `thread_id`:

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

`InMemorySaver` sirve para aprender y tests; al reiniciar el proceso se pierde. En producción usa
un checkpointer persistente soportado y aplica cifrado, autenticación, backup y retención. El
`thread_id` debe pertenecer al usuario autenticado: aceptar uno arbitrario desde el cliente es una
vulnerabilidad de acceso horizontal.

## 4. Ventana deslizante, resumen y selección

Cuando el historial crece hay tres estrategias complementarias:

1. **Ventana:** conserva system + últimos N turnos. Barata, pero olvida acuerdos antiguos.
2. **Resumen acumulativo:** comprime decisiones y hechos estables. Puede introducir deriva.
3. **Selección por relevancia:** recupera recuerdos relacionados con el turno actual.

No resumas todo en un párrafo narrativo. Usa un esquema comprobable:

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

Conserva punteros al turno fuente para auditar el resumen. Regénéralo desde la fuente cuando
cambies el esquema o el modelo de resumen.

## 5. Memoria episódica

Registra eventos relevantes, no transcripciones enteras:

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

Una política de escritura debería responder:

- ¿es útil fuera de esta conversación?
- ¿es estable o solo una preferencia momentánea?
- ¿lo dijo el usuario o lo infirió el modelo?
- ¿es sensible y tenemos base para conservarlo?
- ¿cuándo caduca y cómo se corrige o borra?

Los recuerdos inferidos deben marcarse como tales y tener menor confianza. No conviertas una
frase ambigua en un perfil permanente.

## 6. Memoria semántica

Embebe recuerdos y recupera top-k por similitud, siempre dentro del namespace autorizado:

```text
namespace = (tenant_id, user_id, "preferences")
query = embedding(turno_actual)
candidate_memories = vector_search(namespace, query, top_k=8)
selected = rerank_and_filter(candidate_memories, min_score, not_expired=True)
```

La similitud no basta. Combina:

- scope de tenant/usuario;
- tipo de memoria;
- vigencia;
- importancia;
- confianza y procedencia;
- diversidad para evitar ocho duplicados;
- límite de tokens.

Un recuerdo recuperado es dato no confiable: pudo ser inyectado por un usuario o estar obsoleto.
No debe elevar su prioridad por encima del system prompt ni autorizar acciones.

## 7. Escritura explícita frente a automática

Tres políticas:

- **Explícita:** solo "recuerda que...". Máximo control, menor comodidad.
- **Automática con esquema:** un extractor propone recuerdos y reglas deterministas los filtran.
- **Automática con confirmación:** el agente pregunta antes de guardar datos sensibles o duraderos.

Una buena UX permite "¿qué recuerdas de mí?", editar y olvidar. Sin esas operaciones, la memoria
es opaca y difícil de corregir.

## 8. Seguridad y privacidad

Riesgos principales:

- mezcla de namespaces y fuga entre usuarios;
- conservación indefinida de PII;
- prompt injection persistente almacenada como recuerdo;
- recuerdos falsos que alteran decisiones futuras;
- uso secundario no consentido;
- backups que impiden cumplir borrado.

Controles:

1. autorización en cada lectura/escritura, no solo al iniciar sesión;
2. minimización y allowlist de tipos guardables;
3. cifrado, TTL y borrado propagado;
4. procedencia, confianza y versionado;
5. validación del contenido antes de inyectarlo;
6. auditoría de accesos y cambios;
7. herramientas separadas para leer, escribir y borrar.

Nunca guardes claves, contraseñas, tokens, datos de pago completos ni instrucciones que eleven
privilegios.

## 9. Evaluar memoria

No midas "parece recordar". Crea secuencias multi-turno con ground truth:

- retención de un hecho tras 5, 20 y 50 turnos;
- actualización: el usuario cambia una preferencia;
- contradicción: dos recuerdos con fecha distinta;
- aislamiento: otro usuario pregunta por ese dato;
- olvido: el usuario borra un recuerdo;
- irrelevancia: el dato existe pero no debe entrar en este turno;
- inyección persistente: un mensaje intenta guardarse como instrucción.

Métricas: recall de recuerdos relevantes, precision de recuerdos inyectados, tasa de datos
obsoletos, violaciones de aislamiento, coste de contexto y éxito de tarea.

## 10. Cuándo no necesitas memoria

- la tarea termina en un solo request;
- el dato puede consultarse de forma autoritativa en una DB;
- el usuario no espera personalización;
- el riesgo de conservar supera el beneficio;
- un identificador de sesión y estado explícito resuelven el caso.

Consultar `get_customer_profile()` es mejor que "recordar" el plan de facturación: la DB es la
fuente de verdad y se actualiza sin reconstruir memoria.

## Errores comunes

1. Reenviar todo el chat hasta agotar contexto.
2. Confundir checkpoint con memoria semántica.
3. Guardar inferencias como hechos confirmados.
4. Recuperar globalmente sin namespace por tenant.
5. No invalidar recuerdos cuando cambia la fuente de verdad.
6. Evaluar solo conversaciones felices de tres turnos.
7. Añadir memoria para resolver un problema de estado determinista.

## Para profundizar

- LangGraph, memoria: https://docs.langchain.com/oss/python/langgraph/add-memory
- LangGraph, persistence: https://docs.langchain.com/oss/python/langgraph/persistence
- MemGPT: https://arxiv.org/abs/2310.08560
