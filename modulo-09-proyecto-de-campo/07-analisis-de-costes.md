# Plantilla de análisis de costes

El objetivo es explicar cuánto costó operar el sistema, por qué, cómo cambia a escala y qué palanca
reduciría coste sin cruzar el gate de calidad. Usa factura/usage reales y conserva la tarifa vigente
aplicada; no copies cifras de un tutorial.

## 1. Periodo y unidad económica

Declara:

- periodo UTC, entorno y commit/digest;
- requests totales, exitosas, abstenidas y fallidas;
- unidad principal: coste por tarea completada, no solo por llamada;
- moneda e impuestos incluidos/excluidos;
- fecha y enlaces de cada tarifa oficial;
- créditos/free tiers separados del coste económico real.

## 2. Desglose real

Rellena con datos del dashboard y factura:

| Componente | Unidad | Volumen real | Tarifa vigente | Coste | Fuente/evidencia |
|---|---|---:|---:|---:|---|
| modelo de routing | tokens entrada/salida | | | | |
| modelo de generación | tokens entrada/salida/reasoning | | | | |
| embeddings de ingesta | tokens | | | | |
| embeddings de query | tokens | | | | |
| jueces/evaluación | llamadas/tokens | | | | |
| vector DB | almacenamiento/operaciones | | | | |
| API/compute | horas/vCPU/RAM | | | | |
| observabilidad | eventos/GB | | | | |
| red/egress | GB | | | | |
| monitor/servicios | mes | | | | |
| **total** | | | | | |

Cuenta evaluación, retries y tools: son parte del producto. Muestra créditos en una columna aparte;
si el proveedor regaló 20 €, el coste observado puede ser 0, pero el coste recurrente no lo es.

## 3. Fórmulas reproducibles

Para una llamada:

```text
coste_llm =
  input_uncached_tokens / 1_000_000 * tarifa_input
  + cached_input_tokens / 1_000_000 * tarifa_cached_input
  + output_tokens / 1_000_000 * tarifa_output
  + cargos_de_tools
```

Para una tarea multi-paso:

```text
coste_tarea = suma(coste_llm de cada intento)
             + embeddings_query
             + búsquedas/reranking
             + tools externas
             + porción de infraestructura y observabilidad

coste_por_tarea_exitosa = coste_total_periodo / tareas_exitosas
```

No atribuyas coste compartido dividiendo solo entre requests si batch, ingesta o evaluación sirven a
otro volumen. Explica el driver elegido.

## 4. Distribución, no solo media

Reporta p50/p95/p99 de tokens, llamadas y coste por tarea. Añade:

| Segmento/ruta | tareas | éxito | tokens p50/p95 | coste p50/p95 | motivo |
|---|---:|---:|---:|---:|---|
| cache hit | | | | | |
| Luna/volumen | | | | | |
| Terra/equilibrio | | | | | |
| Sol/insignia | | | | | |
| tool error/retry | | | | | |
| evaluación | | | | | |

Los nombres GPT-5.6 reflejan el catálogo de agosto de 2026. Si cambian, conserva aquí el alias y
snapshot reales del experimento; no reescribas el pasado con el nombre nuevo.

## 5. Proyección 1×, 10× y 100×

Separa coste variable, escalonado y fijo:

| Escenario | tareas/mes | tokens/tarea | cache hit | concurrencia pico | coste variable | infra escalonada | total |
|---|---:|---:|---:|---:|---:|---:|---:|
| observado 1× | | | | | | | |
| crecimiento 10× | | | | | | | |
| crecimiento 100× | | | | | | | |
| estrés (p95 + retries) | | | | | | | |

No multipliques todo linealmente: una instancia salta por escalones, free tiers desaparecen, los
descuentos/batch pueden entrar y rate limits fuerzan otra arquitectura. Incluye un escenario de peor
caso con entrada larga y proveedor inestable.

## 6. Palancas y experimentos

Para cada optimización, calcula ahorro y pérdida/riesgo medidos:

| Palanca | Hipótesis | Ahorro mensual | Impacto calidad | Impacto p95 | Evidencia | Decisión |
|---|---|---:|---:|---:|---|---|
| reducir contexto | | | | | ablation | |
| cache semántico | | | | | falsos hits + hit rate | |
| routing de tiers | | | | | eval pareada | |
| batch para eval/ingesta | | | | | factura/run | |
| modelo local | | | | | coste total GPU | |

Una optimización solo se promueve si mantiene gates críticos. Ahorrar 30 % empeorando abstención de
seguridad no es ahorro: desplaza coste a incidentes.

## 7. Break-even de self-hosting

Compara:

```text
API mensual = volumen_tokens * tarifa_efectiva + herramientas
self-host mensual = GPU + CPU/RAM + disco + egress + observabilidad
                    + horas de operación/guardia + capacidad ociosa
```

Calcula utilización y throughput requeridos, replicas para alta disponibilidad y reserva de picos.
Incluye evaluación del modelo cuantizado. Un modelo que cabe en VRAM pero no supera el gate no es una
alternativa.

## 8. Conclusión ejecutiva

Termina con cinco cifras: coste total, coste medio y p95 por tarea exitosa, driver dominante,
proyección 10× y ahorro de la siguiente palanca aprobada. Añade el mayor riesgo de la proyección y
qué señal te avisará de que el supuesto dejó de cumplirse.
