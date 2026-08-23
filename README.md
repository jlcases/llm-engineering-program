# Ingeniería de Sistemas LLM — ruta abierta de campo

Este repositorio no intenta convertir una tecnología cambiante en un título académico. Es una ruta
autodidacta, pública y versionada para aprender a construir sistemas LLM que se puedan inspeccionar,
medir, detener, recuperar y defender con evidencia. Profesionales en activo mantienen el contenido
mediante pull requests; la historia y la autoría de cada mejora permanecen visibles.

La unidad de progreso no es el tiempo sentado ni un crédito: es un artefacto ejecutable. Cada módulo
termina con una prueba de trabajo que otra persona puede revisar, reproducir y discutir.

## La tesis de la ruta

Un modelo capaz no garantiza un sistema capaz. La ingeniería está en todo lo que lo rodea:

1. **Interfaces** — contexto, contratos de salida, retrieval y tools.
2. **Harnesses** — el entorno legible que entrega capacidades, límites, observabilidad y evals.
3. **Loops** — el control de estado, presupuesto, progreso, parada y recuperación.
4. **Graphs** — las relaciones de ejecución, conocimiento y procedencia que permiten razonar sin
   perder trazabilidad.
5. **Operación** — calidad, coste, seguridad y comportamiento bajo fallos reales.

Ese eje distingue esta ruta de una colección de tutoriales sobre proveedores o frameworks. Los
modelos y librerías son piezas reemplazables; los contratos, las invariantes y la evidencia perduran.

## Stack vigente

Foto revisada el **23 de agosto de 2026**. Los defaults ejecutables son
[gpt-5.6-luna](https://developers.openai.com/api/docs/models) y
[claude-haiku-4-5](https://platform.claude.com/docs/en/about-claude/models/overview); el routing
permite comparar alternativas actuales sin acoplar el código a una marca.

El código nuevo usa OpenAI Responses, Anthropic Messages/tool use, LangGraph 1.2, MCP Python SDK
2.x y RAGAS 0.4.3. Todos los modelos son configurables por `.env`. Las integraciones históricas
aparecen únicamente cuando ayudan a entender una decisión o una migración.

## Mapa del repositorio

| Módulo | Pregunta de ingeniería | Prueba de trabajo | Esfuerzo orientativo |
|---|---|---|---:|
| [01 · Interfaces de modelo](modulo-01-fundamentos-llm/) | ¿Cómo sustituir un modelo sin reescribir el producto? | Cliente multi-proveedor observable | 15–18 h |
| [02 · Contexto y contratos](modulo-02-prompt-engineering/) | ¿Cómo convertir instrucciones y salidas en interfaces testeables? | Regresión A/B de contratos | 38–45 h |
| [03 · Retrieval Engineering](modulo-03-rag/) | ¿Cómo saber qué evidencia se recuperó y por qué? | Retrieval con citas, abstención y métricas | 50–60 h |
| [04 · Interfaces de agentes](modulo-04-agentes/) | ¿Qué puede hacer el modelo y con qué autoridad? | Agente con tools tipadas y MCP | 50–60 h |
| [05 · Harness Engineering](modulo-05-harness-engineering/) | ¿Qué entorno necesita el agente para trabajar de forma verificable? | Harness aislado con eval suite | 25–35 h |
| [06 · Loop Engineering](modulo-06-loop-engineering/) | ¿Cómo progresa, se detiene y se recupera una ejecución? | Loop acotado, duradero e idempotente | 25–35 h |
| [07 · Graph Engineering](modulo-07-graph-engineering/) | ¿Cómo conectar estado, conocimiento y procedencia? | Sistema híbrido de grafos evaluado | 25–35 h |
| [08 · Production Engineering](modulo-08-production-engineering/) | ¿Cómo se comporta el sistema cuando cambia o falla el mundo? | Servicio con SLOs, evals y runbook | 50–60 h |
| [09 · Proyecto de campo](modulo-09-proyecto-de-campo/) | ¿Puedes defender todas las decisiones con evidencia real? | Sistema desplegado y demo reproducible | 47–57 h |

La [ruta de aprendizaje completa](RUTA_DE_APRENDIZAJE.md) explica dependencias, bifurcaciones y
criterios para saltarse material que ya dominas. La preparación de certificaciones vive en
[certificaciones/](certificaciones/) como recorrido opcional, no como centro del producto.

## Cómo trabajar con el repo

1. Prepara el entorno con [setup/README.md](setup/README.md).
2. Ejecuta el diagnóstico de la web o empieza por el módulo cuya prueba de trabajo aún no puedas
   producir.
3. Lee solo la teoría necesaria para construir el artefacto.
4. Ejecuta los labs, rompe los happy paths y conserva trazas, métricas y decisiones.
5. Pide revisión: una afirmación sin evidencia no completa un módulo.

Cada módulo contiene un mapa, teoría, labs, ejercicios con criterios públicos y un proyecto. Las
soluciones editoriales no forman parte del repositorio público. El CI bloquea rutas, claves y
marcadores que puedan revelar una solución activa.

## Del conocimiento público a la web

[llmengineerclub.com](https://llmengineerclub.com) publica la edición inglesa en la raíz y la
española bajo `/es/`. La web añade navegación, progreso local, herramientas, pruebas competitivas y
atribución, pero no convierte el repo en una caja negra: cada página enlaza su fuente y las PR que la
mejoraron.

El progreso ordinario vive en el navegador y no requiere cuenta. Club Quiz es una experiencia
separada con passkey seudónima, tiempo medido en servidor y vinculación social posterior y
voluntaria. Ninguna de las dos experiencias necesita cookies.

## Frontera pública y privada

Este repo contiene conocimiento, enunciados, datos ficticios, rúbricas y tests públicos. No contiene
solucionarios editoriales, claves de simulacros ni el banco activo de preguntas competitivas. Una PR
puede proponer objetivos y blueprints; el material exacto de una edición se transforma y revisa en la
fuente privada de la web y solo vuelve al repo cuando deja de estar activo.

Consulta la [política de contribuciones al Club Quiz](docs/club-quiz-contributions.md) y
[CONTRIBUTING.md](CONTRIBUTING.md). Toda contribución fusionada conserva atribución permanente.

## Validación local

```bash
node scripts/validate-public-content.mjs
node scripts/validate-course-contracts.mjs
node scripts/validate-current-stack.mjs
node scripts/validate-certification-currency.mjs
node scripts/validate-translations.mjs --complete
uv sync --locked --extra dev
uv run ruff check .
uv run python -m compileall -q modulo-* setup translations/en
uv run pytest -q
```

## Punto de entrada

Necesitas experiencia básica programando, HTTP/JSON y Git. Si puedes leer Python pero todavía no
dominas ML, empieza en el módulo 1. Si ya has desplegado un RAG o un agente, usa las pruebas de
trabajo de los módulos 5–8 como diagnóstico: ahí suele estar la distancia entre una demo y un sistema
profesional.
