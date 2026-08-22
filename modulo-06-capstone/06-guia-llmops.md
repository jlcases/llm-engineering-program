# Guía LLMOps del capstone

El entregable no es “tener un dashboard”: es poder detectar, explicar y revertir una degradación
de calidad, coste o fiabilidad. Cada gráfico debe responder una pregunta operacional y enlazar con
una acción o runbook.

## 1. Contrato de telemetría

Propaga un `trace_id` desde la API hasta grafo, tools, retrieval y proveedor. Cada span registra:

| Campo | Ejemplo | Regla |
|---|---|---|
| `trace_id`, `span_id`, `parent_id` | IDs opacos | Nunca email/user ID |
| `operation` / `kind` | `retrieve`, `llm`, `tool` | Vocabulario acotado |
| `model` + snapshot | alias/digest usado | Requerido para reproducir |
| `prompt_version` | `answer-v7` | Hash o versión inmutable |
| `corpus_version` | hash del manifest | Separa cambios de retrieval |
| `duration_ms`, `ttft_ms` | número | Histograma, no solo promedio |
| `input/output/reasoning_tokens` | número | Según metadata del proveedor |
| `estimated_cost` | moneda + tarifa versionada | No cablear una tarifa eterna |
| `status`, `error_code`, `attempt` | valores acotados | Sin stack traces al usuario |
| `tool_name`, `approved` | allowlist + booleano | Sin argumentos sensibles |
| `eval_sampled` | booleano | Une producción y evaluación |

No uses prompt, query, tenant ni error libre como label de Prometheus: crean cardinalidad ilimitada
y filtran datos. El contenido completo solo puede ir a un almacén de trazas con redacción, cifrado,
acceso y retención definidos. Incluye un test con canarios para demostrar que la redacción funciona.

## 2. Las cuatro vistas obligatorias

### Fiabilidad

- tasa HTTP 2xx/4xx/5xx y `task_success`, separadas;
- errores/rate limits/timeouts por proveedor y tool;
- retries, circuit breaker y colas;
- uptime externo y consumo del error budget.

Un 200 con respuesta vacía o sin evidencia es un fallo de tarea. Define `task_success` con un
evaluador o feedback observable, no copiando el status HTTP.

### Latencia

- p50/p95/p99 extremo a extremo;
- TTFT y tiempo total si hay streaming;
- spans de routing, retrieval, reranking, tools y generación;
- distribución por ruta/modelo y cache hit/miss.

Los percentiles se calculan en el backend de métricas sobre histogramas; no promedies p95 de
ventanas. Anota despliegues y cambios de modelo para relacionar causa y efecto.

### Calidad y safety

- doc/chunk recall en suite versionada;
- faithfulness, relevancy y abstención en muestras;
- citas inválidas, tools prohibidas y aprobación omitida;
- tasa/segmentos de feedback negativo;
- ataques bloqueados y falsos positivos de guardrails.

No ejecutes un juez caro en cada request. Muestrea por riesgo, segmento y novedad; ejecuta eval
offline en cada PR y una suite live autorizada de forma periódica.

### Uso y coste

- requests, tokens y coste por modelo/ruta/tenant;
- coste p50/p95 por tarea, no solo total diario;
- cache hit rate y coste evitado estimado;
- presupuesto consumido y proyección al cierre del periodo;
- top de operaciones caras con IDs opacos.

Guarda la tabla de precios usada con `valid_from`, fuente y moneda. Si el proveedor cambia precios,
las series históricas no deben recalcularse silenciosamente.

## 3. SLOs y alertas

Define SLOs antes de ver los resultados. Ejemplo adaptable:

| SLI | SLO | Ventana | Exclusiones explícitas |
|---|---:|---:|---|
| disponibilidad externa | ≥ 99 % | 14 días | mantenimiento anunciado |
| task success | ≥ 97 % | 7 días | tareas fuera de alcance bien abstenidas |
| latencia | p95 < 3 s | rolling 24 h | jobs batch |
| faithfulness muestreada | ≥ 0,75 | última suite válida | casos no respondibles |
| tools prohibidas | 0 | siempre | ninguna |
| coste por query | bajo presupuesto propio | 24 h | backfills autorizados |

Alertas mínimas:

1. burn rate rápido/lento del error budget;
2. p95 por encima del SLO durante dos ventanas;
3. rate limits/timeouts del proveedor;
4. gasto proyectado supera 80 % y 100 % del presupuesto;
5. caída de eval global o de segmento crítico;
6. cualquier tool prohibida, canario filtrado o aprobación omitida;
7. ingesta/indexación sin éxito o corpus version desalineada.

Para cada alerta documenta severidad, owner, canal, query, umbral, ventana, runbook y condición de
cierre. Una alerta sin owner ni acción es ruido.

## 4. Prueba exigida de las alertas

Provoca al menos tres fallos en staging:

- añade 800 ms de latencia controlada para disparar p95;
- configura una credencial inválida/fixture 429 para ejercitar retry y circuit breaker;
- ejecuta la candidata regresiva del dataset para bloquear calidad.

Conserva timestamp, captura/query, trace IDs afectados, notificación recibida, tiempo de detección,
acción, recuperación y aprendizaje. No inyectes fallos destructivos en producción para conseguir
una captura.

## 5. Runbook común

Toda alerta debe llevar a un recorrido corto:

1. confirmar impacto con SLI y ventana, no con una anécdota;
2. identificar primer despliegue/model/prompt/corpus que cambió;
3. abrir una traza representativa y localizar el span dominante;
4. contener: rollback, desactivar ruta/tool, bajar concurrencia o activar fallback;
5. verificar recuperación con la misma señal y una tarea sintética;
6. registrar timeline y convertir el fallo en test/eval.

Separa mitigación de causa raíz. “Reiniciamos” puede recuperar, pero no explica por qué ocurrió.

## 6. Evidencia de entrega

- dashboard exportado como código o JSON y URL/capturas fechadas;
- queries de cada panel y definición de cada métrica;
- tres alertas probadas con su notificación y runbook;
- una traza completa de éxito, error de tool, abstención e intervención humana;
- política de redacción/retención y test de canarios;
- informe de SLO/error budget y versión desplegada durante la ventana.

En la defensa elige un incidente y navega de alerta → métrica → traza → versión → rollback. Esa
cadena causal vale más que veinte paneles decorativos.
