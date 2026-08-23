# Programa de Experto en LLM Engineering e IA Agéntica

Repositorio de estudio autodidacta que cubre, en profundidad y con práctica real, el temario completo de un programa de experto en LLM Engineering (10 ECTS): fundamentos de LLMs, prompt engineering, sistemas RAG, agentes, LLMOps y un proyecto capstone de nivel producción. Incluye preparación para las certificaciones **AWS Certified AI Practitioner (AIF-C01)** y **NVIDIA Certified Associate: Generative AI LLMs (NCA-GENL)**.

## Stack vigente del programa

Foto revisada el **21 de agosto de 2026**. Los defaults ejecutables son
[`gpt-5.6-luna`](https://developers.openai.com/api/docs/models) y
[`claude-haiku-4-5`](https://platform.claude.com/docs/en/about-claude/models/overview); el módulo de
routing compara GPT-5.6 Luna, Terra y Sol. La panorámica incluye Claude Sonnet/Opus 5, Gemini 3.x,
Llama 4, Mistral Small 4 y la familia Qwen actual. GPT-4o, GPT-3 y Llama 3 solo aparecen cuando son
necesarios para explicar historia, papers o tokenizadores, nunca como defaults de una integración
nueva.

El código nuevo usa **OpenAI Responses**, structured outputs y function calling actuales;
**Anthropic Messages/tool use**; **LangGraph 1.2**; **MCP Python SDK 2.x** y **RAGAS 0.4.3**. Todos
los modelos son configurables por `.env`: una actualización del catálogo no exige modificar el
código ni invalida los datasets de evaluación.

## Estructura del repo

| Carpeta | Contenido | ECTS |
|---|---|---|
| [`modulo-01-fundamentos-llm/`](modulo-01-fundamentos-llm/) | Arquitectura transformer, tokenización, parámetros de generación, panorámica de modelos, Amazon Bedrock y APIs de OpenAI/Anthropic | 0,5 |
| [`modulo-02-prompt-engineering/`](modulo-02-prompt-engineering/) | Zero/few-shot, chain-of-thought, function calling, structured outputs (Pydantic + Instructor), evaluación y versionado de prompts | 1,5 |
| [`modulo-03-rag/`](modulo-03-rag/) | RAG de producción: chunking, vector DBs, reranking, RAG avanzado (HyDE, self-RAG, CRAG), evaluación con RAGAS, app full-stack | 2 |
| [`modulo-04-agentes/`](modulo-04-agentes/) | Patrones de agentes (ReAct, reflection), LangGraph, MCP, tool use, multi-agente, memoria, Bedrock Agents, alignment | 2 |
| [`modulo-05-llmops/`](modulo-05-llmops/) | Observabilidad, evaluación continua, optimización de costes, Docker/K8s, vLLM/Ollama, AWS, Responsible AI, seguridad | 2 |
| [`modulo-06-capstone/`](modulo-06-capstone/) | Proyecto final: RAG + agente autónomo desplegado en cloud con LLMOps y costes controlados | 2 |
| [`certificaciones/`](certificaciones/) | Guías de estudio, flashcards y simulacros para AIF-C01 y NCA-GENL | — |
| [`setup/`](setup/) | Entorno de desarrollo, dependencias y claves API | — |
| [`recursos/`](recursos/) | Bibliografía, papers, cursos y enlaces comentados | — |

## Cómo usar este repo

1. **Prepara el entorno** siguiendo [`setup/README.md`](setup/README.md) (Python 3.12 + `uv`, claves API en `.env`).
2. **Sigue los módulos en orden.** Cada módulo tiene:
   - `README.md` — mapa del módulo y objetivos de aprendizaje
   - `teoria/` — apuntes en profundidad, un fichero por tema
   - `labs/` — código ejecutable, un lab por concepto clave
   - `ejercicios.md` — ejercicios propuestos con criterios de aceptación y tests públicos

Las soluciones de referencia no forman parte del repositorio público. La corrección se apoya en
tests, rúbricas y evidencia reproducible para que completar un ejercicio demuestre competencia.
El CI ejecuta `node scripts/validate-public-content.mjs` y bloquea cualquier filtración por ruta o
marcador reservado.
3. **Trabaja las certificaciones en paralelo**: AIF-C01 se cubre en los módulos 1–5 y NCA-GENL en los módulos 2–6. Los enunciados de los simulacros están en `certificaciones/`; la corrección razonada se integra desde la fuente privada de la web.
4. **Cierra con el capstone** del módulo 6, que integra todo lo anterior.

El calendario sugerido y el detalle completo del temario están en [`PLAN_DE_ESTUDIOS.md`](PLAN_DE_ESTUDIOS.md).

## Versión web y progreso

[llmengineerclub.com](https://llmengineerclub.com) transforma este contenido en una experiencia
Astro bilingüe con ruta guiada, buscador, herramientas locales, simulacros, flashcards, diagnóstico
y portfolio. No requiere cuenta: el progreso vive en el navegador. La autoría de cada página se
sincroniza desde las PR fusionadas y enlaza al perfil público de quien creó, mejoró o revisó el
contenido.

El **Club Quiz** es una experiencia voluntaria y separada: ofrece una práctica local con preguntas
retiradas y un único intento oficial por passkey seudónima. La puntuación tiene en cuenta los
aciertos y la velocidad medida en servidor. No usa cookies y el resultado queda privado por
defecto; solo después se puede vincular voluntariamente un perfil social para optar al ranking.
Cada resultado dispone de una prueba Ed25519 verificable.

Este repositorio contiene conocimiento, enunciados, datos ficticios y criterios verificables. Los
solucionarios editoriales de ejercicios se mantienen fuera del repositorio público y del artefacto
web. Las claves de simulacro tampoco viven aquí: la web las combina desde su fuente privada y solo
muestra la corrección después de entregar el examen.

Las PR también pueden proponer objetivos y blueprints para futuras preguntas. El material exacto
de una edición competitiva se transforma y revisa fuera del historial público; cuando se retira,
puede volver aquí como práctica abierta. Consulta la
[política de contribuciones al Club Quiz](docs/club-quiz-contributions.md).

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

La validación de stack rechaza modelos legacy como defaults y obliga a revisar el catálogo del
curso cada 120 días. La de certificaciones fija los contratos publicados de AIF-C01 revisión 1.1
y NCA-GENL y rechaza nomenclatura retirada. La validación bilingüe conserva bloques de código,
destinos de enlaces y el AST ejecutable de cada lab.

Consulta [`CONTRIBUTING.md`](CONTRIBUTING.md) antes de abrir una PR. Toda contribución fusionada
conserva atribución permanente en la web.

## Requisitos previos

- Un año de experiencia en programación full-stack (Python es el lenguaje del repo).
- Fundamentos de ML: modelo, entrenamiento, validación, sobreajuste, métricas.
- APIs REST: HTTP, JSON, autenticación por API key.
- VS Code o Jupyter y Git básico.
- Recomendado: NumPy/pandas, SQL, algo de AWS y haber usado ChatGPT/Claude en contexto técnico.

## Salidas profesionales que cubre el temario

LLM Engineer / AI Engineer · RAG Systems Engineer · AI Agents Developer · AI Product Engineer · Consultor/freelance de IA.
