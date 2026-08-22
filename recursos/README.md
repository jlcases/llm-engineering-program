# Recursos y bibliografía

Referencias transversales al programa, comentadas. Cada módulo tiene además su propia sección "Para profundizar" al final de cada fichero de teoría.

## Papers fundacionales

- **Attention Is All You Need** (Vaswani et al., 2017) — el paper del transformer. Léelo tras la teoría del módulo 1.
- **Language Models are Few-Shot Learners** (Brown et al., 2020, GPT-3) — origen del few-shot prompting.
- **Chain-of-Thought Prompting Elicits Reasoning** (Wei et al., 2022) y **Self-Consistency** (Wang et al., 2022) — base del módulo 2.
- **Retrieval-Augmented Generation for Knowledge-Intensive NLP** (Lewis et al., 2020) — el paper de RAG.
- **ReAct: Synergizing Reasoning and Acting** (Yao et al., 2022) — el patrón de agente que implementarás a mano en el módulo 4.
- **Constitutional AI** (Bai et al., Anthropic, 2022) — alignment, módulo 4.

## Documentación oficial imprescindible

- Guías de prompting de **Anthropic** (docs.claude.com) y **OpenAI** (platform.openai.com/docs) — las mejores guías prácticas que existen; releerlas cada pocos meses.
- **Building effective agents** (Anthropic) — el ensayo de referencia sobre cuándo usar agentes y cuándo no.
- **Model Context Protocol** — modelcontextprotocol.io (spec y SDKs).
- **LangGraph** — langchain-ai.github.io/langgraph.
- **RAGAS** — docs.ragas.io.
- **Amazon Bedrock** — docs.aws.amazon.com/bedrock.
- **OWASP Top 10 for LLM Applications** — genai.owasp.org (módulo 5).

## Cursos complementarios gratuitos

- **DeepLearning.AI short courses** (deeplearning.ai/short-courses) — píldoras de 1-2 h sobre prompting, RAG, agentes, evals; útiles como refuerzo por módulo.
- **AWS Skill Builder** — ruta oficial gratuita para AIF-C01.
- **fast.ai Practical Deep Learning** — si necesitas reforzar los fundamentos de DL previos al programa.

## Newsletters y seguimiento del estado del arte

El panorama de modelos cambia cada pocos meses: apóyate en las release notes de OpenAI/Anthropic/Google/Meta, en LMSYS Chatbot Arena para comparativas vivas, y desconfía de cualquier tabla estática de benchmarks (incluidas las de este repo si alguna vez las hubiera).

## Cómo estudiar este programa

1. **Teoría → lab → ejercicios**, en ese orden, por cada tema. No pases al siguiente tema sin haber ejecutado y roto el lab (cambia parámetros, provoca errores, mide).
2. **Un cuaderno de notas propio** (`notas/` está en .gitignore si quieres crearla): explicar un concepto con tus palabras es el mejor test de comprensión.
3. **Commits por tema**: trata tu avance como un proyecto real; el historial de git es tu registro de estudio.
4. **Los simulacros de certificación, en frío**: hazlos con reloj y sin mirar apuntes, y repasa después las áreas falladas con las guías por dominio.
