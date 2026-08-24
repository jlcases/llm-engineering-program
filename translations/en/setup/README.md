# Environment Setup

## 1. Python and Dependencies

Requires Python ≥ 3.12 and [`uv`](https://docs.astral.sh/uv/).

```bash
cd llm-engineering-program
uv sync --locked --all-extras
source .venv/bin/activate
```

`uv sync --locked` installs only the module 1–2 base. Use `--all-extras` so the RAG, agent,
harness, and production labs never depend on packages that happen to exist on your machine.

Alternative without uv:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e '.[rag,agents,ops,dev]'
```

## 2. API Keys

Copy the template and fill in only the keys you will use in each module:

```bash
cp setup/.env.example .env
```

| Variable | Where to get it | Used from |
|---|---|---|
| `OPENAI_API_KEY` | platform.openai.com | Module 1 |
| `ANTHROPIC_API_KEY` | console.anthropic.com | Module 1 |
| `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` / `AWS_REGION` | AWS Console (IAM) | Module 1 (Bedrock) |
| `COHERE_API_KEY` | dashboard.cohere.com | Module 3 (rerank) |
| `LANGSMITH_API_KEY` | smith.langchain.com | Module 8 (`--send` only) |

The labs load `.env` with `python-dotenv`. **Never** upload `.env` to the repo (it is already in `.gitignore`).

## 3. Estimated API Costs

Cost depends on the current catalog and pricing. The August 2026 examples use
`gpt-5.6-luna` and `claude-haiku-4-5` for volume, reserving higher tiers for
justified comparisons. Check the official price before each run and set a
budget; modules 3–5 also include offline workflows or local models with Ollama.

## 4. Optional Local Services

- **Ollama** (`brew install ollama`) — local models for deployment labs and for working without API costs.
- **Docker Desktop** — required in module 8 (containers) and for local Qdrant/pgvector in module 3.
- **Node ≥ 20** — only for the Next.js frontend in module 3.

## 5. Verification

```bash
python setup/check_env.py --profile all
```

Check the Python version, dependencies for the selected profile, and configured API keys.

## 6. Instructor Compatibility

The main environment sets the current OpenAI SDK 3.x. Instructor 1.15.4, the version
current as of 21-08-2026, declares `openai<3` and `rich<15`; installing it in the same environment
would make the lock unresolvable. The structured outputs lab uses the native API by default and
keeps the comparison with Instructor in an isolated process:

```bash
uv run --no-project \
  --with-requirements setup/requirements-instructor.txt \
  python modulo-02-prompt-engineering/labs/05_structured_outputs_instructor.py \
  --backend instructor
```

This does not change the model (`OPENAI_MODEL=gpt-5.6-luna`); it only isolates incompatible SDK
versions. The requirements file makes the decision reproducible.

RAGAS 0.4.3 pulls the same dependency. Additionally, `langchain-community<0.4` is pinned: RAGAS still
imports `chat_models.vertexai`, a module removed in the 0.4.x branch. Its live mode runs in an
isolated manner with lexical retrieval to avoid mixing a second embedding stack:

```bash
uv run --no-project \
  --with-requirements setup/requirements-ragas.txt \
  python modulo-03-rag/labs/06_evaluacion_ragas.py \
  --ragas --lexical --limit 5
```

The `--offline` mode of the lab belongs to the main environment and does not require RAGAS or API keys.
