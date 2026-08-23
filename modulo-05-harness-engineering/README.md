# Módulo 05 — Harness Engineering

> El modelo propone. El harness decide qué puede ver, qué puede hacer, qué queda registrado y cómo
> se demuestra que el resultado es válido.

Un agent harness convierte un modelo generalista en un sistema capaz de trabajar dentro de un
entorno concreto. Un evaluation harness ejecuta tareas comparables, conserva trayectorias y estados
finales, aplica graders y agrega resultados. Confundir ambos produce sistemas que parecen mejorar
cuando en realidad ha cambiado el entorno de prueba.

## Qué aprenderás

1. Separar con precisión modelo, agent harness, evaluation harness y eval suite.
2. Diseñar contratos estables para tareas, capacidades, estado, trazas y outcomes.
3. Hacer que contexto y herramientas sean descubribles sin inundar la ventana de contexto.
4. Aplicar mínimos privilegios, aislamiento por tarea y aprobación antes de efectos sensibles.
5. Ejecutar trials independientes y distinguir calidad del agente de ruido del entorno.
6. Clasificar runtimes, productos integrados, ADEs y orquestadores antes de compararlos.
7. Diseñar benchmarks causales que separen mecanismo, outcome end-to-end y composición.
8. Mantener el harness como producto: versionado, drift, deuda y eliminación de capacidades obsoletas.

## Mapa del módulo

| Paso | Lectura | Lab | Decisión que debes poder defender |
|---:|---|---|---|
| 1 | [`01-anatomia-y-contratos.md`](teoria/01-anatomia-y-contratos.md) | — | Qué pertenece al modelo, al harness y al producto |
| 2 | [`02-contexto-capacidades-y-aislamiento.md`](teoria/02-contexto-capacidades-y-aislamiento.md) | [`01_capability_harness.py`](labs/01_capability_harness.py) | Qué puede descubrir y ejecutar cada run |
| 3 | [`03-trazas-y-evaluation-harness.md`](teoria/03-trazas-y-evaluation-harness.md) | [`02_eval_harness.py`](labs/02_eval_harness.py) | Cómo comparar trials sin contaminación |
| 4 | [`04-panorama-de-harnesses-actuales.md`](teoria/04-panorama-de-harnesses-actuales.md) | [`03_harness_landscape.py`](labs/03_harness_landscape.py) | Qué productos compiten, se complementan o viven en otra capa |
| 5 | [`05-benchmarking-de-harnesses.md`](teoria/05-benchmarking-de-harnesses.md) | Suite causal | Qué afirmación permite realmente cada comparación |
| 6 | [`ejercicios.md`](ejercicios.md) | Tests propios | Qué falla cuando una frontera se rompe |
| 7 | [`proyecto/README.md`](proyecto/README.md) | Integración | Si el harness mejora capacidad sin ampliar autoridad |

## Vocabulario operativo

| Concepto | Contrato mínimo |
|---|---|
| **Task** | Instrucción, estado inicial, capacidades, presupuesto y criterio de salida |
| **Capability** | Nombre, esquema, efecto, permisos, timeout y errores posibles |
| **Run** | Identidad, versión del harness, estado, eventos y outcome terminal |
| **Trial** | Un run aislado de una tarea dentro de una evaluación |
| **Trajectory** | Secuencia observable de decisiones, llamadas, resultados y transiciones |
| **Outcome** | Cambio verificable en el entorno, no solo el texto final |
| **Grader** | Función independiente que mide una propiedad concreta del trial |

## Prueba de trabajo

Entrega un harness local que:

- carga un manifiesto de capacidades por tarea;
- bloquea tools no permitidas y paths fuera del workspace;
- exige aprobación para un efecto configurable;
- redacta secretos antes de persistir trazas;
- ejecuta trials en entornos limpios y concurrentes;
- evalúa output, estado final y fugas del entorno por separado;
- genera un informe que incluye versión, latencia, fallos y muestras revisables;
- compara al menos dos runtimes de la misma cohorte y una composición runtime-orquestador;
- conserva hechos, hipótesis, configuración efectiva y fuentes primarias por separado.

El happy path no basta. Debes demostrar al menos: capability inexistente, permiso ausente, path
traversal, tool que falla, output excesivo, fixture contaminado y grader que discrepa del texto final.

## Criterio de salida

Has completado el módulo cuando otra persona puede ejecutar la misma suite dos veces y explicar qué
cambió en el agente, qué cambió en el harness y qué variación pertenece al entorno. Si esas tres
causas siguen mezcladas en una única puntuación, todavía no tienes un harness fiable.

## Fuentes primarias

- [OpenAI — Harness engineering](https://openai.com/index/harness-engineering/)
- [Anthropic — Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
- [Anthropic — Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps)
- [DeepSeek Harness — Architecture](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/architecture.md)
- [Pi Agent Harness](https://github.com/earendil-works/pi)
- [Aider — Edit formats](https://aider.chat/docs/more/edit-formats.html)
