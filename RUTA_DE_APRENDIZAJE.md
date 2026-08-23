# Ruta de aprendizaje — Ingeniería de Sistemas LLM

> Esta ruta no acredita horas ni obliga a seguir un calendario. El esfuerzo es orientativo; la
> salida de cada módulo es una prueba de trabajo reproducible.

La secuencia sigue las dependencias reales de un sistema, no la taxonomía de un proveedor. Puedes
entrar en cualquier punto si produces su prueba de trabajo y superas los casos negativos asociados.

## Tres tramos, nueve pruebas

| Tramo | Módulos | Cambio que debes demostrar |
|---|---|---|
| **Construir interfaces** | 01–03 | El modelo, el contexto y el conocimiento son componentes medibles y reemplazables. |
| **Dar capacidad sin perder control** | 04–07 | El agente actúa dentro de un harness, un loop y unos grafos con invariantes explícitas. |
| **Operar y defender** | 08–09 | El sistema conserva calidad, coste y seguridad bajo carga, cambios y fallos. |

## 01 — Interfaces de modelo y fundamentos

Aprende lo suficiente del modelo para diseñar una interfaz que sobreviva a su sustitución.

- Transformer, atención, tokenización y límites de contexto.
- Parámetros de generación y su efecto medido, no folklore.
- APIs de OpenAI, Anthropic y Amazon Bedrock detrás de un contrato propio.
- Streaming, errores, rate limits, uso de tokens, latencia y metadatos.
- Selección de modelos mediante evals representativas de la tarea.

**Prueba de trabajo:** cliente multi-proveedor que conserva el mismo contrato y registra tokens,
latencia, errores y versión del modelo.

## 02 — Contexto y contratos de salida

Deja de tratar el prompt como texto mágico: conviértelo en una interfaz versionada.

- Jerarquía de instrucciones, delimitación y ensamblado de contexto.
- Few-shot y razonamiento observable sin almacenar cadenas privadas de pensamiento.
- Tool calling con esquemas estrictos y errores explícitos.
- Structured outputs, validación, repair acotado y compatibilidad de versiones.
- Datasets, graders, comparación A/B y gates de regresión.
- Inyección de instrucciones, datos no confiables y separación de autoridad.

**Prueba de trabajo:** pipeline que compara dos versiones del contrato sobre el mismo dataset y
bloquea una regresión significativa en CI.

## 03 — Retrieval Engineering

Construye una cadena de evidencia cuyo fallo pueda localizarse antes de culpar al generador.

- Ingesta, normalización, chunking y metadatos con identidad estable.
- Embeddings, búsqueda densa, léxica e híbrida.
- Recall de candidatos, reranking y límites de cada etapa.
- Citas, abstención, frescura, conflicto y defensa ante inyección indirecta.
- Evaluación separada de retrieval, grounding y respuesta final.
- GraphRAG como opción para preguntas relacionales o globales, no como default.

**Prueba de trabajo:** sistema con conjunto etiquetado, métricas de retrieval, citas verificables,
casos no respondibles y análisis de fallos por etapa.

## 04 — Interfaces de agentes y tools

Define qué puede hacer el modelo antes de optimizar cuántas cosas intenta hacer.

- Diferencia entre workflow, agente y automatización convencional.
- Patrones ReAct, plan-execute, evaluator-optimizer y delegación.
- Tools pequeñas, tipadas, observables y con errores accionables.
- MCP: negociación de capacidades, tools, resources y lifecycle.
- Memoria de trabajo, episódica y semántica con políticas de retención.
- Multi-agente solo cuando la separación de contexto o autoridad lo justifica.
- Aprobación humana e idempotencia para efectos externos.

**Prueba de trabajo:** agente con tres tools y un servidor MCP propio que demuestra permisos,
trazas, errores recuperables y rechazo de acciones no autorizadas.

## 05 — Harness Engineering

El harness es el sistema alrededor del modelo que convierte capacidad general en trabajo fiable.

- Frontera entre modelo, agent harness y evaluation harness.
- Contexto legible: mapas, contratos, estado y artefactos versionados.
- Manifiesto de capacidades y descubrimiento progresivo de tools.
- Sandbox, mínimos privilegios, allowlists y puntos de aprobación.
- Entornos aislados por tarea, fixtures deterministas y limpieza posterior.
- Trazas estructuradas de entradas, decisiones, tools, resultados y estado final.
- Evals end-to-end con tareas, trials, outcomes y graders independientes.
- Mantenimiento del harness: detectar entropía, drift y capacidades ausentes.

**Prueba de trabajo:** harness local que ejecuta tareas aisladas, restringe capacidades, produce una
traza portable y genera un informe de eval reproducible.

## 06 — Loop Engineering

Un loop profesional no es un `while True`: es un protocolo de control con estados terminales.

- Contrato de transición: estado, observación, decisión, acción y resultado.
- Presupuestos simultáneos de pasos, tiempo, tokens, coste y efectos.
- Criterios de éxito, imposibilidad, agotamiento, cancelación y escalado humano.
- Señales de progreso y detección de ciclos improductivos.
- Taxonomía de errores, retry budget, backoff y circuit breakers.
- Idempotency keys, deduplicación y semántica de efectos.
- Checkpoints, journal de eventos, reanudación y compatibilidad de versión.
- Concurrencia, backpressure y orden de resultados.

**Prueba de trabajo:** loop duradero que completa, agota presupuesto, cancela y reanuda sin repetir
un efecto aceptado, con tests para cada transición terminal.

## 07 — Graph Engineering

Usa grafos cuando la relación sea parte del problema, no para añadir una dependencia de moda.

- Tres planos distintos: grafo de ejecución, grafo de conocimiento y grafo de procedencia.
- Nodos, aristas, tipos, cardinalidad, identidad e invariantes.
- Grafos de estado con ramas, ciclos, checkpoints e interrupciones.
- Extracción de entidades, resolución de identidad y evolución temporal.
- Claims enlazados a evidencia, versión y autoridad de la fuente.
- Retrieval híbrido: texto, vectores, vecinos y caminos con presupuesto.
- Comunidades y resúmenes globales al estilo GraphRAG.
- Métricas de cobertura, precisión de aristas, path relevance y procedencia.

**Prueba de trabajo:** sistema que responde una consulta relacional mediante evidencia textual y
grafo, conserva la procedencia de cada claim y compara el resultado con un baseline sin grafo.

## 08 — Production Engineering para sistemas LLM

Opera el sistema completo, incluido todo aquello que el modelo no controla.

- Trazas, métricas, logs y correlación entre calidad y operación.
- Evaluación continua, canary datasets y drift.
- Routing, caching, batching y presupuestos de coste.
- Contenedores, despliegue, escalado y modelos locales.
- SLOs de latencia, disponibilidad, calidad y coste.
- Threat modeling, prompt injection, secretos y aislamiento de tenants.
- Privacidad, auditoría, governance y respuesta ante incidentes.

**Prueba de trabajo:** servicio desplegado con dashboard, alertas, evals de regresión, análisis de
costes, threat model y runbook probado mediante un incidente simulado.

## 09 — Proyecto de campo

Integra solo la complejidad que puedas justificar con datos y fallos reproducibles.

- Problema y usuario reales; alcance que pueda terminarse.
- Arquitectura y ADRs que registran alternativas y trade-offs.
- Retrieval o contexto externo con procedencia.
- Agente con autoridad acotada dentro de su harness y loop.
- Grafos únicamente cuando mejoren una consulta o una decisión medida.
- Despliegue temprano para acumular métricas de operación.
- Demo reproducible, postmortem y defensa técnica.

**Prueba de trabajo:** repositorio ejecutable, URL o paquete desplegable, dataset de eval, trazas,
dashboard, costes, runbook y una defensa que incluya al menos un fallo que cambió el diseño.

## Rutas opcionales

- **Certificaciones:** repasa los blueprints oficiales después de construir los fundamentos; no
  sustituyen las pruebas de trabajo.
- **Contribución:** mejora una fuente, un lab o una rúbrica mediante PR y participa en su revisión.
- **Club Quiz:** practica o compite con tiempo de servidor; el ranking mide recuperación bajo presión,
  no sustituye la evidencia de ingeniería.

## Regla para avanzar

No avances porque hayas leído el último fichero. Avanza cuando puedas enseñar el artefacto, ejecutar
sus tests felices y adversos, explicar una decisión que descartaste y señalar qué evidencia te haría
cambiar de opinión.
