# Curriculum — LLM Engineering and Agentic AI Expert (10 ECTS)

> 1 ECTS ≈ 25–30 hours of work. Estimated total: 250–300 hours. At a pace of 10 h/week, approximately 6–7 months; at 20 h/week, approximately 3 months.

## Suggested Schedule (10 h/week pace)

| Weeks | Module | ECTS | Milestone |
|---|---|---|---|
| 1–2 | I. LLM Fundamentals and APIs | 0.5 | Working multi-provider client (OpenAI, Anthropic, Bedrock) |
| 3–6 | II. Advanced Prompt Engineering | 1.5 | Prompt evaluation pipeline with test dataset and A/B testing |
| 7–12 | III. RAG Systems and Evaluation | 2 | Full-stack RAG app with RAGAS ≥ 0.75 on faithfulness |
| 13–18 | IV. AI Agents and Orchestration | 2 | Multi-agent system with LangGraph + custom MCP server |
| 19–24 | V. LLMOps, Production, and Responsible AI | 2 | Module III/IV system deployed, monitored, and with measured costs |
| 25–30 | VI. Capstone | 2 | Complete cloud system + AIF-C01 and NCA-GENL practice exams |

---

## Module I — LLM Fundamentals and APIs (0.5 ECTS)

Transformer architecture, tokenization, and generation parameters. Overview of current models and first exposure to Amazon Bedrock and the OpenAI and Anthropic APIs.

- Transformer architecture: encoder, decoder, and multi-head attention
- Tokenization: BPE, WordPiece, cross-model comparison
- Generation parameters: temperature, top_p, top_k, penalties
- Model landscape: GPT-5.6, Claude 5/4.5, Gemini 3.x, Llama 4, and Mistral Small 4
- AWS AI services: Bedrock, SageMaker JumpStart, and Amazon Q
- Amazon Bedrock: foundation models, inference, and API

## Module II — Advanced Prompt Engineering (1.5 ECTS)

From zero-shot to few-shot, chain-of-thought, function calling, and structured outputs with Pydantic and Instructor. Prompt evaluation using test datasets and A/B testing, prompt management and versioning, and bias and hallucination detection.

> Note: the original brochure erroneously repeats the Module I bullets here; this repo expands on the actual syllabus described in the module paragraph.

- Core techniques: zero-shot, few-shot, chain-of-thought, self-consistency
- System prompts, roles, and context scoping
- Function calling / tool use in OpenAI and Anthropic
- Structured outputs: JSON mode, Pydantic, Instructor
- Prompt evaluation: test datasets, LLM-as-judge, A/B testing
- Prompt management and versioning (registries, templates, CI)
- Bias and hallucination detection and mitigation

## Module III — RAG Systems and Evaluation (2 ECTS)

Complete production-grade RAG architecture, from ingestion to generation. Rigorous evaluation with RAGAS and Bedrock Knowledge Bases as a managed service.

- RAG architecture: ingestion, embedding, indexing, and retrieval
- Vector databases: Pinecone, Weaviate, Qdrant, pgvector
- Chunking strategies: fixed, semantic, hierarchical, late
- Reranking: cross-encoders, Cohere Rerank, ColBERT
- Advanced RAG: HyDE, multi-query, self-RAG, CRAG
- Amazon Bedrock Knowledge Bases: managed RAG on AWS
- RAG evaluation: RAGAS, faithfulness, relevance, context recall
- Hallucination detection: metrics, tools, and mitigation
- Full-stack RAG app: FastAPI + Next.js + vector DB

## Module IV — AI Agents and Orchestration (2 ECTS)

Agents capable of planning, reasoning, and using tools. Multi-agent systems with LangGraph and MCP. Memory, flow control, and reliability evaluation.

- Agent patterns: ReAct, plan-execute, reflection, self-critique
- LangGraph: state graphs, cycles, conditionals, and checkpoints
- Model Context Protocol (MCP): architecture and server development
- Advanced tool use: tool design, error handling
- Multi-agent systems: coordination, supervisors, communication
- Agent memory: episodic, semantic, and working
- Amazon Bedrock Agents: action groups, integrated knowledge bases
- Agent evaluation: determinism, costs, and safety guardrails
- Alignment: RLHF, RLAIF, Constitutional AI, and fine-tuning techniques

## Module V — LLMOps, Production, and Responsible AI (2 ECTS)

Operation and deployment of LLM systems in production; observability, continuous evaluation, costs, Docker/K8s, Responsible AI, and security.

- LLM observability: traces, spans, metrics, and alerts
- Continuous evaluation: eval pipelines and regression testing
- Cost optimization: semantic caching, routing, and batching
- Docker for LLMs: containers, multi-stage build, optimization
- Open-source LLM deployment: vLLM, Ollama, Triton Inference
- AWS: ECS Fargate, Lambda, SageMaker endpoints, and CloudWatch
- Responsible AI: bias, fairness, transparency, and explainability
- Security and governance: IAM, KMS, CloudTrail, VPC endpoints
- Production safety: guardrails, moderation, and abuse monitoring

## Module VI — Final Project / Capstone (2 ECTS)

Design, implementation, evaluation, and deployment of a complete system: production RAG + autonomous agent orchestrating multiple tools, deployed on cloud, monitored, and with controlled costs.

Deliverables:

1. Architecture document: technical diagram, ADRs, and stack justification
2. Complete RAG pipeline with RAGAS evaluation ≥ 0.75
3. Autonomous agent with ≥ 3 tools and documented LangSmith traces
4. Cloud deployment: public URL, uptime ≥ 99%, P95 latency < 3 s
5. LLMOps dashboard: cost/query, faithfulness, latency, and alerts
6. Cost analysis: actual breakdown and scaling projection
7. AWS AIF-C01 practice exam: 65 questions with review of improvement areas
8. NCA-GENL preparation: five weighted areas, ten topics, flashcards, and 50-question practice exam
9. Live demo (20 min) + code review + technical defense (15 min Q&A)

---

## Certifications

- **AWS Certified AI Practitioner (AIF-C01)** — covered in modules 1–5. Material at [`certificaciones/aws-aif-c01/`](certificaciones/aws-aif-c01/).
- **NVIDIA Certified Associate: Generative AI LLMs (NCA-GENL)** — covered in modules 2–6. Material at [`certificaciones/nvidia-nca-genl/`](certificaciones/nvidia-nca-genl/).
