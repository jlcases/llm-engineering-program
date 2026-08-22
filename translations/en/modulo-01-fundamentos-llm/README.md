# Module I — LLMs and APIs Fundamentals (0.5 ECTS)

> Estimated time: **15–18 hours** (weeks 1–2 of the program).
> Milestone: a **multi-provider client** capable of invoking OpenAI, Anthropic, and
> Amazon Bedrock behind a custom interface, logging tokens, latency, and stop reason.

This module builds the technical vocabulary you will use throughout the program. It does not
aim for you to train a transformer from scratch: it aims for you to understand what happens between the input text
and the next token, to anticipate the effect of tokenization and sampling parameters, and to know how to integrate three APIs without obscuring their key differences.

## Learning Objectives

By the end, you should be able to:

1. Explain the decoder-only architecture, self-attention, causal mask, KV cache, and context
   cost without relying on flawed analogies.
2. Tokenize text, measure cross-lingual differences, and estimate the impact on context and cost.
3. Select `temperature`, `top_p`, and output limits based on the task, always verifying the
   stop reason.
4. Parse responses from OpenAI and Anthropic, including typed content and token usage.
5. Invoke a foundation model using the Amazon Bedrock Converse API without hardcoding credentials.
6. Encapsulate providers under a custom contract without stripping their metadata or errors.
7. Choose a model family and size based on a real-world evaluation, not an isolated benchmark ranking.

## Structure

```text
modulo-01-fundamentos-llm/
├── README.md
├── teoria/
│   ├── 01-arquitectura-transformer.md
│   ├── 02-tokenizacion.md
│   ├── 03-parametros-generacion.md
│   ├── 04-panoramica-modelos.md
│   └── 05-aws-ia-bedrock.md
├── labs/
│   ├── 01_primer_llamada_openai.py
│   ├── 02_primer_llamada_anthropic.py
│   ├── 03_tokenizacion_comparada.py
│   ├── 04_parametros_generacion.py
│   └── 05_bedrock_inference.py
└── ejercicios.md              ← enunciados y criterios verificables
```

## Recommended Order

| # | Theory | Practice | Hours |
|---|---|---|---:|
| 1 | [Transformer Architecture](teoria/01-arquitectura-transformer.md) | Exercise 1 | 3 |
| 2 | [Tokenization](teoria/02-tokenizacion.md) | [Lab 03](labs/03_tokenizacion_comparada.py) + Exercises 2–3 | 3 |
| 3 | [Generation Parameters](teoria/03-parametros-generacion.md) | [Lab 04](labs/04_parametros_generacion.py) + Exercises 4–5 | 3 |
| 4 | [Model Landscape](teoria/04-panoramica-modelos.md) | [Labs 01–02](labs/) + Exercises 6–7 | 3 |
| 5 | [AWS AI and Bedrock](teoria/05-aws-ia-bedrock.md) | [Lab 05](labs/05_bedrock_inference.py) + Exercise 8 | 2 |
| 6 | Integration | Exercises 9–10: multi-provider client | 3+ |

## Preparation and Execution

First, complete the [general setup](../setup/README.md). Labs 03 and the attention exercises
are local. Labs 01, 02, and 04 consume a small amount of API. Lab 05
requires an AWS account with explicit access to the chosen model and may incur costs.

```bash
uv sync
source .venv/bin/activate
python modulo-01-fundamentos-llm/labs/03_tokenizacion_comparada.py
```

Model names can be changed via `OPENAI_MODEL`, `ANTHROPIC_MODEL`, and
`BEDROCK_MODEL_ID`. Model aliases change over time: before running a saved course
that has been sitting for months, verify availability and pricing in the official documentation.

## Pass Criteria

- You can explain to another person the attention calculation of a single head and solve Exercise 1.
- You have run all five labs and triggered at least one truncation or controlled error case.
- The client from Exercise 10 returns the same result type for all three providers,
  preserves useful original metadata, and contains no hardcoded keys in the code.
- You can justify, through a mini-evaluation, which model you would use for a specific task.
