# LLM Engineering and Agentic AI Expert Program

Self-study repository covering, in depth and with real-world practice, the full syllabus of an LLM Engineering expert program (10 ECTS): LLM fundamentals, prompt engineering, RAG systems, agents, LLMOps, and a production-level capstone project. Includes preparation for the **AWS Certified AI Practitioner (AIF-C01)** and **NVIDIA Certified Associate: Generative AI LLMs (NCA-GENL)** certifications.

## Current Program Stack

Stack snapshot reviewed on **August 21, 2026**. The executable defaults are
[`gpt-5.6-luna`](https://developers.openai.com/api/docs/models) and
[`claude-haiku-4-5`](https://platform.claude.com/docs/en/about-claude/models/overview); the routing module compares GPT-5.6 Luna, Terra, and Sol. The panorama includes Claude Sonnet/Opus 5, Gemini 3.x,
Llama 4, Mistral Small 4, and the current Qwen family. GPT-4o, GPT-3, and Llama 3 appear only when needed to explain history, papers, or tokenizers—never as defaults for a new integration.

New code uses current **OpenAI Responses**, structured outputs, and function calling;
**Anthropic Messages/tool use**; **LangGraph 1.2**; **MCP Python SDK 2.x**; and **RAGAS 0.4.3**. All models are configurable via `.env`: updating the catalog requires neither code changes nor invalidating evaluation datasets.

## Repo Structure

| Folder | Content | ECTS |
|---|---|---|
| [`modulo-01-fundamentos-llm/`](modulo-01-fundamentos-llm/) | Transformer architecture, tokenization, generation parameters, model landscape, Amazon Bedrock, and OpenAI/Anthropic APIs | 0.5 |
| [`modulo-02-prompt-engineering/`](modulo-02-prompt-engineering/) | Zero/few-shot, chain-of-thought, function calling, structured outputs (Pydantic + Instructor), prompt evaluation and versioning | 1.5 |
| [`modulo-03-rag/`](modulo-03-rag/) | Production RAG: chunking, vector DBs, reranking, advanced RAG (HyDE, self-RAG, CRAG), RAGAS evaluation, full-stack app | 2 |
| [`modulo-04-agentes/`](modulo-04-agentes/) | Agent patterns (ReAct, reflection), LangGraph, MCP, tool use, multi-agent, memory, Bedrock Agents, alignment | 2 |
| [`modulo-05-llmops/`](modulo-05-llmops/) | Observability, continuous evaluation, cost optimization, Docker/K8s, vLLM/Ollama, AWS, Responsible AI, security | 2 |
| [`modulo-06-capstone/`](modulo-06-capstone/) | Final project: RAG + autonomous agent deployed on cloud with LLMOps and controlled costs | 2 |
| [`certificaciones/`](certificaciones/) | Study guides, flashcards, and mock exams for AIF-C01 and NCA-GENL | — |
| [`setup/`](setup/) | Development environment, dependencies, and API keys | — |
| [`recursos/`](recursos/) | Bibliography, papers, courses, and annotated links | — |

## How to Use This Repo

1. **Set up the environment** by following [`setup/README.md`](setup/README.md) (Python 3.12 + `uv`, API keys in `.env`).
2. **Follow the modules in order.** Each module includes:
   - `README.md` — module map and learning objectives
   - `teoria/` — in-depth notes, one file per topic
   - `labs/` — executable code, one lab per key concept
   - `ejercicios.md` — proposed exercises with acceptance criteria and public tests

Reference solutions are not part of the public repository. Grading relies on
tests, rubrics, and reproducible evidence so that completing an exercise demonstrates competence.
CI runs `node scripts/validate-public-content.mjs` and blocks any leakage via path or
reserved marker.
3. **Work on certifications in parallel:** AIF-C01 is covered in modules 1–5 and NCA-GENL in modules 2–6. Mock-exam questions are in `certificaciones/`; the reasoned grading key is integrated from the website's private source.
4. **Finish with the capstone** in module 6, which integrates everything above.

The suggested schedule and full syllabus details are in [`PLAN_DE_ESTUDIOS.md`](PLAN_DE_ESTUDIOS.md).

## Web Version and Progress

[llmengineerclub.com](https://llmengineerclub.com) transforms this content into an
Astro bilingual experience with a guided path, search, local tools, mock exams, flashcards, a skills assessment,
and portfolio. No account required: progress lives in the browser. Page authorship is
synchronized from merged PRs and links to the public profile of whoever created, improved, or reviewed the
content.

The **Club Quiz** is a separate, voluntary experience: it offers a local practice run with retired
questions and one official attempt per pseudonymous passkey. Scoring takes both correct answers and
server-measured response speed into account. It uses no cookies and the result is private by default;
only afterwards may a participant voluntarily link a social profile to enter the leaderboard. Every
result has a verifiable Ed25519 proof.

This repository contains knowledge, problem statements, fictional data, and verifiable criteria. Editorial
exercise solutions are kept outside both the public repository and the web artifact. Mock-exam keys do not
live here either: the website combines them from its private source and only reveals the review after an exam
is submitted.

PRs may also propose objectives and blueprints for future questions. The exact material for a competitive
edition is transformed and reviewed outside the public history; after retirement, it may return here as open
practice. Read the [Club Quiz contribution policy](docs/club-quiz-contributions.md).

## Local Validation

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

Stack validation rejects legacy models as defaults and requires a course catalog review every 120 days. Certification validation pins the published contracts for AIF-C01 revision 1.1 and NCA-GENL and rejects retired nomenclature. Bilingual validation preserves code blocks, link destinations, and the executable AST of each lab.

Consult [`CONTRIBUTING.md`](CONTRIBUTING.md) before opening a PR. Every merged contribution retains permanent attribution on the web.

## Prerequisites

- One year of full-stack programming experience (Python is the repo language).
- ML fundamentals: model, training, validation, overfitting, metrics.
- REST APIs: HTTP, JSON, API key authentication.
- VS Code or Jupyter and basic Git.
- Recommended: NumPy/pandas, SQL, some AWS experience, and prior hands-on use of ChatGPT or Claude in a technical context.

## Professional roles covered by the syllabus

LLM Engineer / AI Engineer · RAG Systems Engineer · AI Agents Developer · AI Product Engineer · AI Consultant/freelancer.
