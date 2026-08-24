# LLM Systems Engineering — an open field path

This repository does not try to turn a fast-moving technology into an academic title. It is a
self-directed, public, versioned path for learning to build LLM systems that can be inspected,
measured, stopped, recovered, and defended with evidence. Working practitioners maintain the
content through pull requests; the history and authorship of every improvement remain visible.

The unit of progress is not seat time or a credit: it is an executable artifact. Every module ends
with proof of work that another person can review, reproduce, and challenge.

## The path's thesis

A capable model does not guarantee a capable system. The engineering lives in everything around it:

1. **Interfaces** — context, output contracts, retrieval, and tools.
2. **Harnesses** — the legible environment that supplies capabilities, limits, observability, and evals.
3. **Loops** — control over state, budget, progress, stopping, and recovery.
4. **Graphs** — execution, knowledge, and provenance relationships that support reasoning without
   losing traceability.
5. **Operations** — quality, cost, security, and behavior under real failures.

This axis separates the path from a collection of provider or framework tutorials. Models and
libraries are replaceable pieces; contracts, invariants, and evidence endure.

## Current stack

Snapshot reviewed on **August 23, 2026**. The executable defaults are
[gpt-5.6-luna](https://developers.openai.com/api/docs/models) and
[claude-haiku-4-5](https://platform.claude.com/docs/en/about-claude/models/overview); routing lets
you compare current alternatives without coupling the code to one brand.

New code uses OpenAI Responses, Anthropic Messages/tool use, LangGraph 1.2, MCP Python SDK 2.x, and
RAGAS 0.4.3. Every model is configurable through `.env`. Historical integrations appear only when
they help explain a decision or migration.

## Repository map

| Module | Engineering question | Proof of work | Suggested effort |
|---|---|---|---:|
| [01 · Model interfaces](modulo-01-fundamentos-llm/) | How can a model be replaced without rewriting the product? | Observable multi-provider client | 15–18 h |
| [02 · Context and contracts](modulo-02-prompt-engineering/) | How do instructions and outputs become testable interfaces? | A/B contract regression | 38–45 h |
| [03 · Retrieval Engineering](modulo-03-rag/) | How do you know what evidence was retrieved and why? | Retrieval with citations, abstention, and metrics | 50–60 h |
| [04 · Agent interfaces](modulo-04-agentes/) | What may the model do, and under whose authority? | Agent with typed tools and MCP | 50–60 h |
| [05 · Harness Engineering](modulo-05-harness-engineering/) | What environment lets an agent work verifiably? | Isolated harness with an eval suite | 25–35 h |
| [06 · Loop Engineering](modulo-06-loop-engineering/) | How does an execution progress, stop, and recover? | Bounded, durable, idempotent loop | 25–35 h |
| [07 · Graph Engineering](modulo-07-graph-engineering/) | How do state, knowledge, and provenance connect? | Evaluated hybrid graph system | 25–35 h |
| [08 · Production Engineering](modulo-08-production-engineering/) | How does the system behave when the world changes or fails? | Service with SLOs, evals, and a runbook | 50–60 h |
| [09 · Field project](modulo-09-proyecto-de-campo/) | Can every decision be defended with real evidence? | Deployed system and reproducible demo | 47–57 h |

The [complete learning path](RUTA_DE_APRENDIZAJE.md) explains dependencies, branches, and criteria
for skipping material you already master. Certification preparation lives under
[certificaciones/](certificaciones/) as an optional route, not the center of the product.

## How to work with the repository

1. Prepare the environment with [setup/README.md](setup/README.md).
2. Run the site's diagnostic or begin with the module whose proof of work you cannot yet produce.
3. Read only the theory required to build the artifact.
4. Run the labs, break the happy paths, and retain traces, metrics, and decisions.
5. Request review: a claim without evidence does not complete a module.

Each module contains a map, theory, labs, exercises with public criteria, and a project. Editorial
solutions are not part of the public repository. CI blocks paths, keys, and markers that could reveal
an active solution.

## From public knowledge to the web

[llmengineerclub.com](https://llmengineerclub.com) publishes the English edition at the root and the
Spanish edition under `/es/`. The site adds navigation, local progress, tools, competitive tests, and
attribution, but it does not turn the repository into a black box: every page links to its source and
the pull requests that improved it.

Ordinary progress lives in the browser and needs no account. Club Quiz is a separate experience with
a pseudonymous passkey, server-measured time, and optional social linking after completion. Neither
experience needs cookies.

## Public and private boundary

This repository contains knowledge, task statements, fictional data, rubrics, and public tests. It
does not contain editorial solutions, mock-exam keys, or the active competitive question bank. A
pull request may propose objectives and blueprints; the exact material for an edition is transformed
and reviewed in the site's private source and returns to the repository only after it is retired.

Read the [Club Quiz contribution policy](docs/club-quiz-contributions.md) and
[CONTRIBUTING.md](CONTRIBUTING.md). Every merged contribution keeps permanent attribution.

## Local validation

```bash
node scripts/validate-public-content.mjs
node scripts/validate-course-contracts.mjs
node scripts/validate-current-stack.mjs
node scripts/validate-certification-currency.mjs
node scripts/validate-translations.mjs --complete
node --test scripts/tests/*.test.mjs
uv lock --check
uv sync --locked --all-extras
uv run python setup/check_env.py --profile all
uv run ruff check .
uv run python -m compileall -q modulo-* setup translations/en
uv run bandit -q -r modulo-* setup -x '*/tests/*' -ll
bash scripts/smoke-production-container.sh
uv run coverage erase
uv run coverage run -m pytest -q
uv run coverage json -o coverage.json
node scripts/validate-coverage.mjs coverage.json
uv run pip-audit --strict
uv run pip-audit --strict --requirement modulo-08-production-engineering/docker/requirements.txt --disable-pip --require-hashes
bash scripts/audit-isolated-requirements.sh
```

## Entry point

You need basic programming, HTTP/JSON, and Git experience. If you can read Python but do not yet
understand ML, begin with module 1. If you have already deployed a RAG system or an agent, use the
proof-of-work gates in modules 5–8 as your diagnostic: that is usually where the distance between a
demo and a professional system becomes visible.
