# Exercises — Module II

The exercises are designed to produce reusable artifacts. Save prompts, datasets, and
results with versioning. Do not optimize against the visible examples until you have memorized the test.

## 1. Zero-shot with contract

Design a prompt to extract from emails: intent (`cancelar`, `cambiar`, `consultar`, `otro`),
optional identifier, and urgency. Define input, output, criteria, and abstention. Create 12 cases,
including 3 ambiguous ones, and measure accuracy per field before adding examples.

## 2. Few-shot selection

Choose four examples for exercise 1. Justify coverage, diversity, and order. Compare:

- fixed examples;
- examples selected by similarity;
- one example per class.

Evaluate on the same cases and record extra tokens.

## 3. Self-consistency with budget

Expand lab 02 to 20 problems with verifiable answers. Compare 1, 3, 5, and 9 samples. Report
accuracy, agreement, tokens, and cost. Decide the minimum number of samples that exceeds your gate.

## 4. Hierarchy and hostile content

Construct 15 inputs where the delimited text attempts to change role, format, or reveal instructions.
Compare a naive system prompt with one that defines boundaries and abstention. Do not call the
second "safe": report attack rate, false positives, and remaining failures.

## 5. Tool loop in OpenAI

Add a payment history tool and a dispute creation tool to lab 03. The implementation must:

- require explicit confirmation linked to the invoice and amount;
- use an idempotency key;
- validate state and permissions in code;
- simulate a lost response after creating the dispute, ensuring it is not duplicated upon retry.

## 6. Port tool use to Anthropic

Implement the same tools from exercise 5 using the Messages API. Document the differences between
`function_call_output` and `tool_result`, parallel calls, arguments, and stop signal. Add a
test where a tool returns an error.

## 7. Pydantic contract with cross-field rules

Extract a reservation with `start_date`, `end_date`, assistants, and literal evidence. Validate that the end date is
after the start date, that assistants have no duplicates, and that each optional field allows `null`.
Compare `.responses.parse` and Instructor against three incomplete inputs.

## 8. Golden dataset

Expand `prompt_eval_cases.json` to 60 cases without superficial duplicates. Include segments, critical
cases, dialects, and out-of-scope inputs. Define an annotation guide and have another person
annotate 15 cases; record disagreements and resolve them before evaluation.

## 9. Versioned PromptSpec

Implement the `PromptSpec` from topic 06 with:

- SHA-256 hash of the package;
- variable validation;
- schema version;
- JSON serialization without secrets;
- changelog and compatibility.

Write tests for missing/extra variables and stable hashing.

## 10. Gate in CI

Convert lab 06 into two jobs:

1. offline and without secrets on every PR;
2. authorized live evaluation with a cost limit.

The gate must block global regression > 2 points, critical recall < 95 %, any invalid format
and estimated cost over budget. Save results as an artifact.

## 11. Counterfactual pairs

Create 30 pairs where only the perceived name, regional variant, or age changes. Evaluate label, priority,
tone, and length. Randomize order and repeat three times. Report gap with interval and manually review
all discordant pairs.

## 12. Mini-project — prompt evaluation pipeline

Choose a real task and deliver:

```text
proyecto-prompt/
├── prompts/               # baseline y candidata con metadata
├── schemas/               # contratos Pydantic/JSON Schema
├── data/                  # train/dev/test separados
├── evaluate.py            # métricas programáticas + judge calibrado
├── compare.py             # comparación pareada e intervalos
├── tests/                 # sin red
├── results/               # un run reproducible
└── README.md              # hipótesis, coste, riesgos y decisión
```

Minimum gates:

- at least 50 cases and 5 segments;
- valid schema ≥ 99 %;
- primary metric and critical segment defined before the run;
- paired comparison, not two unmatched means;
- cost/tokens/latency measured;
- analysis of five specific failures;
- rollback by version.

Submission is not approved for "candidate wins": it is approved if the decision is substantiated and the pipeline would detect a real regression.
