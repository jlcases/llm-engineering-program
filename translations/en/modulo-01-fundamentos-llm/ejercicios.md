# Exercises — Module I

Do them in order. Exercises 1–8 consolidate concepts; 9–10 are the module milestone. Record measurements and decisions, not just screenshots showing a script finished.

## 1. Manual Attention

With a single head and dimension 2:

```text
Q = [[1, 0], [0, 1]]
K = [[1, 0], [1, 1]]
V = [[2, 0], [0, 4]]
```

Calculate `softmax(QKᵀ / √2)V` for both tokens. Repeat applying causal masking to the first token.
Explain what changes and why.

**Criterion:** intermediate matrices, row-wise softmax, and approximate numerical result.

## 2. Context Budget

With `o200k_base`, measure tokens for three texts of at least 1,000 characters each: Spanish, English, and code. For a hypothetical window of 32,000 tokens, reserve 2,000 for output and 1,500 for system, tools, and overhead. Calculate how many complete texts fit and document the actual margin.

## 3. Safe Truncation

Implement `truncate_to_tokens(text: str, limit: int, encoding_name: str) -> str`. It must validate that
`limit >= 0`, never exceed the limit when re-encoding, and handle Unicode. Add tests for empty strings,
emoji, Spanish, and code.

## 4. Statistically Reproducible Sampling

Run lab 04 five times per temperature setting. Do not compare exact equality: define two diversity metrics (e.g., unique token ratio and Jaccard similarity between samples) and plot the distribution. Explain why `temperature=0` is not a cryptographic guarantee.

## 5. Output Truncation

Force a very low `max_tokens`/output limit in OpenAI and Anthropic. Detect the stop reason and return a domain error `IncompleteGeneration` instead of partial text. Decide when it would make sense to continue and when to restart.

## 6. Common Provider Contract

Define a `LLMResult` with text, real model, input/output tokens, stop reason, latency, and provider. Adapt labs 01–02 without losing metadata. Write a test with fake clients.

## 7. Mini Model Evaluation

Create 20 cases for a specific task (classification, extraction, or short Q&A). Compare two models using the same prompt and reasonable parameters. Report quality metric, invalid format, p50/p95 latency, and token counts. Choose the cheapest model that exceeds your threshold, without using external rankings as the result.

## 8. Bedrock and Least Privilege

Write an IAM policy for lab 05 that only allows `bedrock:InvokeModel` and `bedrock:InvokeModelWithResponseStream` on the chosen model/inference profile. Explain which resource and region you must adapt. Run `--dry-run` first and, if you have an account, a real call.

## 9. Conversation Context Capacity

Implement a counter that receives messages and a budget. It must reserve output, warn at 80%, and propose which old turns to summarize without removing the system message or the last turn. Compare exact counting for one provider with an estimate for another and clearly label the uncertainty.

## 10. Mini-project — Multi-provider Client

Build a CLI with a common interface for OpenAI, Anthropic, and Bedrock:

```bash
python cliente_multi_proveedor.py --provider openai --prompt "¿Qué es una KV cache?"
python cliente_multi_proveedor.py --provider anthropic --prompt "¿Qué es una KV cache?"
python cliente_multi_proveedor.py --provider bedrock --prompt "¿Qué es una KV cache?"
```

Requirements:

- CLI selection without `if` scattered throughout the application;
- models configurable by environment;
- common `LLMResult` and visible metadata;
- timeout/errors translated into useful messages without leaking secrets;
- optional JSONL logging with latency/tokens, not the prompt by default;
- tests with fakes that do not call APIs;
- README with authentication, cost, and limitations.

**Success criteria:** all three implementations satisfy the same contract, and a provider outage is not confused with an empty response.
