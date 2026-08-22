# Plan de estudios — Experto en LLM Engineering e IA Agéntica (10 ECTS)

> 1 ECTS ≈ 25–30 horas de trabajo. Total estimado: 250–300 horas. A un ritmo de 10 h/semana, unos 6–7 meses; a 20 h/semana, unos 3 meses.

## Calendario sugerido (ritmo 10 h/semana)

| Semanas | Módulo | ECTS | Hito de salida |
|---|---|---|---|
| 1–2 | I. Fundamentos LLM y APIs | 0,5 | Cliente propio multi-proveedor (OpenAI, Anthropic, Bedrock) funcionando |
| 3–6 | II. Prompt engineering avanzado | 1,5 | Pipeline de evaluación de prompts con dataset de test y A/B testing |
| 7–12 | III. RAG systems y evaluación | 2 | App RAG full-stack con RAGAS ≥ 0,75 en faithfulness |
| 13–18 | IV. AI Agents y orquestación | 2 | Sistema multi-agente con LangGraph + servidor MCP propio |
| 19–24 | V. LLMOps, producción y Responsible AI | 2 | Sistema del módulo III/IV desplegado, monitorizado y con costes medidos |
| 25–30 | VI. Capstone | 2 | Sistema completo en cloud + simulacros AIF-C01 y NCA-GENL |

---

## Módulo I — Fundamentos LLM y APIs (0,5 ECTS)

Arquitectura transformer, tokenización y parámetros de generación. Panorámica de modelos actuales y primer contacto con Amazon Bedrock y las APIs de OpenAI y Anthropic.

- Arquitectura transformer: encoder, decoder y atención multi-cabeza
- Tokenización: BPE, WordPiece, comparativa entre modelos
- Parámetros de generación: temperature, top_p, top_k, penalties
- Panorámica de modelos: GPT-5.6, Claude 5/4.5, Gemini 3.x, Llama 4 y Mistral Small 4
- Servicios AWS IA: Bedrock, SageMaker JumpStart y Amazon Q
- Amazon Bedrock: foundation models, inference y API

## Módulo II — Prompt engineering avanzado (1,5 ECTS)

De zero-shot a few-shot, chain-of-thought, function calling y structured outputs con Pydantic e Instructor. Evaluación de prompts con datasets de test y A/B testing, gestión y versionado de prompts, y detección de sesgos y alucinaciones.

> Nota: el folleto original repite aquí por error los bullets del módulo I; este repo desarrolla el temario real descrito en el párrafo del módulo.

- Técnicas base: zero-shot, few-shot, chain-of-thought, self-consistency
- Prompts de sistema, roles y delimitación de contexto
- Function calling / tool use en OpenAI y Anthropic
- Structured outputs: JSON mode, Pydantic, Instructor
- Evaluación de prompts: datasets de test, LLM-as-judge, A/B testing
- Gestión y versionado de prompts (registries, plantillas, CI)
- Detección y mitigación de sesgos y alucinaciones

## Módulo III — RAG systems y evaluación (2 ECTS)

Arquitectura completa de RAG de nivel producción, de la ingestión a la generación. Evaluación rigurosa con RAGAS y Bedrock Knowledge Bases como servicio gestionado.

- Arquitectura RAG: ingestion, embedding, indexado y retrieval
- Bases de datos vectoriales: Pinecone, Weaviate, Qdrant, pgvector
- Estrategias de chunking: fixed, semantic, hierarchical, late
- Reranking: cross-encoders, Cohere Rerank, ColBERT
- RAG avanzado: HyDE, multi-query, self-RAG, CRAG
- Amazon Bedrock Knowledge Bases: RAG gestionado en AWS
- Evaluación RAG: RAGAS, faithfulness, relevance, context recall
- Detección de alucinaciones: métricas, herramientas y mitigación
- Full-stack RAG app: FastAPI + Next.js + vector DB

## Módulo IV — AI Agents y orquestación (2 ECTS)

Agentes capaces de planificar, razonar y usar herramientas. Multi-agente con LangGraph y MCP. Memoria, control de flujos y evaluación de fiabilidad.

- Patrones de agentes: ReAct, plan-execute, reflection, self-critique
- LangGraph: grafos de estado, ciclos, condicionales y checkpoints
- Model Context Protocol (MCP): arquitectura y desarrollo de servidores
- Tool use avanzado: diseño de herramientas, manejo de errores
- Sistemas multi-agente: coordinación, supervisores, comunicación
- Memoria de agentes: episódica, semántica y de trabajo
- Amazon Bedrock Agents: action groups, knowledge bases integradas
- Evaluación de agentes: determinismo, costes y safety guardrails
- Alignment: RLHF, RLAIF, Constitutional AI y técnicas de fine-tuning

## Módulo V — LLMOps, producción y Responsible AI (2 ECTS)

Operación y despliegue de sistemas LLM en producción; observabilidad, evaluación continua, costes, Docker/K8s, Responsible AI y seguridad.

- Observabilidad LLM: trazas, spans, métricas y alertas
- Evaluación continua: pipelines de eval y regression testing
- Optimización de costes: caching semántico, routing y batching
- Docker para LLMs: contenedores, multi-stage build, optimización
- Despliegue de LLMs open-source: vLLM, Ollama, Triton Inference
- AWS: ECS Fargate, Lambda, SageMaker endpoints y CloudWatch
- Responsible AI: sesgo, fairness, transparencia y explicabilidad
- Seguridad y governance: IAM, KMS, CloudTrail, VPC endpoints
- Safety en producción: guardrails, moderación y monitoreo de abusos

## Módulo VI — Proyecto final / Capstone (2 ECTS)

Diseño, implementación, evaluación y despliegue de un sistema completo: RAG de producción + agente autónomo orquestando múltiples herramientas, desplegado en cloud, monitorizado y con costes controlados.

Entregables:

1. Documento de arquitectura: diagrama técnico, ADRs y justificación del stack
2. Pipeline RAG completo con evaluación RAGAS ≥ 0,75
3. Agente autónomo con ≥ 3 herramientas y trazas LangSmith documentadas
4. Despliegue en cloud: URL pública, uptime ≥ 99%, latencia P95 < 3 s
5. Dashboard LLMOps: coste/query, faithfulness, latencia y alertas
6. Análisis de costes: desglose real y proyección a escala
7. Simulacro AWS AIF-C01: 65 preguntas con repaso de áreas de mejora
8. Preparación NCA-GENL: cinco áreas ponderadas, diez temas, flashcards y simulacro de 50 preguntas
9. Demo en vivo (20 min) + code review + defensa técnica (15 min Q&A)

---

## Certificaciones

- **AWS Certified AI Practitioner (AIF-C01)** — se cubre en los módulos 1–5. Material en [`certificaciones/aws-aif-c01/`](certificaciones/aws-aif-c01/).
- **NVIDIA Certified Associate: Generative AI LLMs (NCA-GENL)** — se cubre en los módulos 2–6. Material en [`certificaciones/nvidia-nca-genl/`](certificaciones/nvidia-nca-genl/).
