# Module 02 — Context and output contracts

> Suggested effort: **38–45 hours**.
> Proof of work: **contract evaluation pipeline with a dataset and A/B comparison** running end to end.

Context and output form a system interface. This module moves from “writing prompts that seem to work” to designing **versioned contracts**: instructions with explicit authority, structured outputs, and an evaluation system proving with data whether one version is better than another.

## Learning Objectives

By the end of this module, you should be able to:

1. Selectively choose between zero-shot, few-shot, chain-of-thought, and self-consistency based on the task, and justify when **not** to use each technique.
2. Structure robust system prompts using roles, delimiters, and XML tags, ensuring resilience against hostile or ambiguous inputs.
3. Implement function calling / tool use in both the OpenAI and Anthropic APIs, including the complete tool execution loop.
4. Obtain structured and validated outputs using JSON mode, `response_format`, Pydantic, and Instructor, with automatic retries on validation failure.
5. Build a prompt evaluation pipeline: test dataset, programmatic metrics, LLM-as-judge, and A/B testing with basic statistical rigor.
6. Manage prompts as software artifacts: templates, versioning, registries, and CI evaluation.
7. Detect and mitigate biases and hallucinations at the prompt level.

## Module Structure

```
modulo-02-prompt-engineering/
├── README.md                  ← estás aquí
├── teoria/                    ← apuntes, un fichero por tema
├── labs/                      ← código ejecutable, un lab por concepto
│   └── data/                  ← datasets pequeños para los labs
└── ejercicios.md              ← 12 ejercicios + mini-proyecto final y rúbrica
```

## Recommended Study Order

Follow the theory and lab for each block in pairs: read the topic, run the lab, modify it, and only then move to the next one.

| # | Theory | Associated Lab | Hours |
|---|---|---|---|
| 1 | [`teoria/01-tecnicas-base.md`](teoria/01-tecnicas-base.md) — zero-shot, few-shot, CoT, self-consistency | [`labs/01_zero_vs_few_shot.py`](labs/01_zero_vs_few_shot.py) · [`labs/02_chain_of_thought.py`](labs/02_chain_of_thought.py) | 6 |
| 2 | [`teoria/02-system-prompts-y-contexto.md`](teoria/02-system-prompts-y-contexto.md) — system prompts, roles, XML, delimiters | (applies to all subsequent labs) | 4 |
| 3 | [`teoria/03-function-calling.md`](teoria/03-function-calling.md) — tool use in OpenAI and Anthropic | [`labs/03_function_calling_openai.py`](labs/03_function_calling_openai.py) · [`labs/04_tool_use_anthropic.py`](labs/04_tool_use_anthropic.py) | 7 |
| 4 | [`teoria/04-structured-outputs.md`](teoria/04-structured-outputs.md) — JSON mode, `response_format`, Pydantic, Instructor | [`labs/05_structured_outputs_instructor.py`](labs/05_structured_outputs_instructor.py) | 5 |
| 5 | [`teoria/05-evaluacion-de-prompts.md`](teoria/05-evaluacion-de-prompts.md) — test datasets, LLM-as-judge, A/B testing | [`labs/06_eval_prompts_dataset.py`](labs/06_eval_prompts_dataset.py) · [`labs/07_ab_testing_prompts.py`](labs/07_ab_testing_prompts.py) | 8 |
| 6 | [`teoria/06-versionado-y-gestion.md`](teoria/06-versionado-y-gestion.md) — templates, registries, prompts in CI | (exercises 9–10) | 4 |
| 7 | [`teoria/07-sesgos-y-alucinaciones.md`](teoria/07-sesgos-y-alucinaciones.md) — detection and mitigation at the prompt level | (exercises 11–12) | 4 |
| 8 | [`ejercicios.md`](ejercicios.md) — final mini-project: custom evaluation pipeline | — | 2+ |

Hours include reading, running, and modifying the labs. The final mini-project can grow as much as you like: it is the module's milestone.

## Before You Begin

1. Environment set up according to [`../setup/README.md`](../setup/README.md) (`uv sync` + `.env` in the repo root).
2. You need `OPENAI_API_KEY` and `ANTHROPIC_API_KEY` only for live modes. The development values verified in August 2026 are `gpt-5.6-luna` and `claude-haiku-4-5`; you can override them in `.env`. Estimate the cost using the current official rate before running large-scale evaluations.
3. Labs can be run from the repo root or from this directory; it makes no difference: they load the `.env` from the root via absolute path.

```bash
source .venv/bin/activate
python modulo-02-prompt-engineering/labs/01_zero_vs_few_shot.py
```

## Alignment with Certifications

- **AWS AIF-C01** — Domain 3 (Applications of Foundation Models) directly addresses prompting techniques, and Domain 4 covers bias and hallucination mitigation.
- **NVIDIA NCA-GENL** — The "Prompt Engineering" domain covers zero/few-shot, CoT, and output formatting.

Once you complete the module, complete the corresponding flashcards in [`../certificaciones/`](../certificaciones/).
