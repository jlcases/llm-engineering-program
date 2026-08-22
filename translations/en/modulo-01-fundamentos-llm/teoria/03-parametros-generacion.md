# Generation parameters: temperature, top_p, top_k, and penalties

> **Module 1 · Topic 3** · Estimated study time: 2.5 h
> Associated lab: `labs/04_parametros_generacion.py`
> Associated exercises: 4 and 5.

---

## 1. The starting point: a probability distribution

At the end of topic 1, we saw that an LLM, at each generation step, does not produce "a
word": it produces a **logit** (a real-valued score) for *each token in the vocabulary*.
The softmax converts these logits into probabilities:

```
P(token_i) = e^(z_i) / Σ_j e^(z_j)
```

Generation consists of **sampling** a token from that distribution, adding it to the
sequence, and repeating. All the parameters in this topic do exactly one thing:
**modify the distribution before sampling**. They do not change what the model "knows";
they change how risky it is when choosing.

**Analogy.** The model is a pianist who, at each note, clearly knows which options fit
and how well. Temperature decides how much it improvises; top_p and top_k prohibit it from
playing absurd notes; penalties prevent it from repeating the same riff in a loop.

---

## 2. Temperature: the main lever

The temperature `T` divides the logits before the softmax:

```
P(token_i) = e^(z_i / T) / Σ_j e^(z_j / T)
```

- `T < 1` → amplifies differences between logits → the distribution **sharpens**
(the favorite captures most probability). Output becomes more deterministic and conservative.
- `T = 1` → distribution as produced by the model.
- `T > 1` → flattens the distribution → more mass to unlikely tokens. Output becomes more diverse
  and, past a certain point, incoherent.
- `T = 0` → limit case: *greedy decoding*, always the most probable token.

### 2.1 Numerical Example

Three candidate tokens with logits `gato = 2.0`, `perro = 1.0`, `loro = 0.1`:

| | z/T | e^(z/T) | Probability |
|---|---|---|---|
| **T = 1.0** | 2.0 / 1.0 / 0.1 | 7.39 / 2.72 / 1.11 | **0.66 / 0.24 / 0.10** |
| **T = 0.5** | 4.0 / 2.0 / 0.2 | 54.6 / 7.39 / 1.22 | **0.86 / 0.12 / 0.02** |
| **T = 2.0** | 1.0 / 0.5 / 0.05 | 2.72 / 1.65 / 1.05 | **0.50 / 0.30 / 0.19** |

With T=0.5, "gato" goes from 66% to 86%; with T=2, "loro" nearly doubles its options.
Note that the **order never changes** — temperature does not reorder candidates, it only
redistributes probability among them.

### 2.2 T = 0 does not guarantee total determinism

With T=0 sampling is greedy, but in practice two identical calls may differ
slightly: there is non-determinism due to server-side batching, floating-point
arithmetic, and model updates behind the same name. OpenAI offers `seed` as
a "best effort" for reproducibility. Treat it as *almost* deterministic, never as
a cryptographic guarantee. You will verify this empirically in exercise 4.

---

## 3. Truncating the tail: top_k and top_p

The problem with increasing temperature is the **long tail**: a vocabulary has 100K+
tokens, and although each absurd token has a minuscule probability, the sum of thousands of
absurd tokens is relevant. A single bad sampled token derails everything that follows
(the error feeds itself: the model continues coherently its own nonsense).

### 3.1 top_k

Keep only the `k` most probable tokens, renormalize and sample among them.
Simple, but rigid: `k = 40` can be too permissive when the distribution is
concentrated ("The capital of France is...") and too restrictive when it is flat
("Write a first verse...").

### 3.2 top_p (nucleus sampling)

Instead of a fixed number of candidates, fix a **cumulative probability mass**:
sort tokens from highest to lowest probability and keep the smallest set that
sums to ≥ `p`. With `top_p = 0.9`:

- Concentrated distribution: `[0.85, 0.10, 0.03, ...]` → 2 tokens survive.
- Flat distribution: `[0.08, 0.07, 0.06, ...]` → dozens survive.

The cutoff **adapts to the model's confidence** at each step; that is why top_p (proposed
in Holtzman et al. 2019, *The Curious Case of Neural Text Degeneration*) replaced top_k
as the default truncation method. OpenAI and Anthropic APIs expose `top_p`; `top_k` is
exposed by Anthropic, Bedrock, and most local stacks (llama.cpp, vLLM, Ollama).

### 3.3 Order of application and practical rule

The typical pipeline is: logits → temperature → top_k → top_p → sampling. They interact
with each other, which is why **the universal recommendation (included in OpenAI's documentation)
is to adjust temperature *or* top_p, not both at once**: changing both makes it impossible
to attribute behavioral changes to a single cause.

---

## 4. Penalties: combating repetition

LLMs tend to loop ("very very very...") because repeating what has already been generated
is often locally probable. Two classic mechanisms (OpenAI API, range -2.0 to 2.0):

- **frequency_penalty**: subtracts from each logit an amount **proportional to the number of
times** that token has already appeared. Penalizes persistent repetition.
- **presence_penalty**: subtracts a **fixed** amount if the token has appeared at least once.
Pushes toward introducing new topics/vocabulary, even if the token appeared only once.

```
logit_final = logit - freq_penalty · count(token) - pres_penalty · [count(token) > 0]
```

Negative values do the opposite (encourage repetition). In practice: start at 0;
if you see loops, try 0.1-0.5 for frequency_penalty. High values (>1) produce texts
that avoid normal words in an unnatural way. The Anthropic API does not expose these
penalties (Claude models are trained not to need them); local stacks
usually also offer `repetition_penalty` (multiplicative, HF/vLLM style).

---

## 5. The remaining panel controls

- **max_tokens**: the token limit for *output*. It is not a target ("write 500 tokens")
  but a ceiling: if reached, the response arrives **truncated** — always verify this
   (`finish_reason == "length"` in OpenAI, `stop_reason == "max_tokens"` in Anthropic).
  In Anthropic, this parameter is mandatory.
- **stop / stop_sequences**: strings that halt generation when encountered. Useful for
  delimiting formats (stop at `"\n\n"`, in `"```"`, en `"FIN"`).
- **seed** (OpenAI): best-effort reproducibility attempt, combined with
  `system_fingerprint` to detect backend changes.
- **logprobs**: returns the log-probabilities of generated tokens (and the
  top-N alternatives). Gold for debugging: it teaches you *how confident* the model was at
  each step. Foundation for hallucination detection techniques and calibrated classification.
- **n** (OpenAI): number of alternative responses per call.

---

## 6. Recipes by use case

There are no magic values, but there are sensible starting points:

| Use case | temperature | Others | Why |
|---|---|---|---|
| Data extraction, classification | 0 - 0.2 | — | You want the modal, reproducible response |
| Code | 0 - 0.3 | — | A creative token = a bug |
| RAG / factual response | 0 - 0.4 | — | Fidelity to sources |
| General-purpose chat | 0.7 - 1.0 | top_p 0.9-1 | Naturalness without derailing |
| Creative writing, brainstorming | 1.0 - 1.3 | top_p 0.95 | Diversity; generates multiple samples |
| Varied synthetic data | 1.0+ | presence_penalty > 0 | Prevent all samples from looking alike |

Two important nuances in 2026:

1. **Reasoning models do not always expose these parameters.** Some ignore
   or reject `temperature`/`top_p` except in specific modes; with Claude's *extended thinking*,
   `temperature` must be set to 1. The "thinking" sampling is controlled by
   the provider.
2. **The temperature range depends on the API**: OpenAI accepts 0-2; Anthropic 0-1.
   A "0.7" does not mean exactly the same thing across providers; recalibrate when migrating.

---

## 7. See it with your own eyes

The `04_parametros_generacion.py` lab runs the same prompt with a grid of
temperatures (0, 0.4, 0.8, 1.2) and multiple samples per value, and displays side by side
the variability. Things to look for when running it:

- With T=0, samples are (almost) identical.
- Diversity grows non-linearly: the jump from 0.8 to 1.2 is greater than from 0 to 0.4.
- Coherence remains surprisingly good even with high T *if* top_p
  cuts off the tail — try increasing top_p to 1 with T=1.2 and compare.

---

## 8. Common Errors

1. **Adjusting temperature and top_p simultaneously** without being able to explain what changed. Change one at a time.
2. **T=0 for creative tasks**: you get the most cliché response possible (the modal
   response is, by definition, the most predictable).
3. **High T for extraction/JSON**: a single improbable token breaks parsing. For structured
   output: low T and, preferably, *structured outputs* (module 3).
4. **Interpreting max_tokens as a target length** without checking the stop reason.
   Truncated responses in production are almost always due to this.
5. **Relying on T=0 as absolute determinism** for tests. Use semantic assertions,
   not string equality.
6. **Copying values between providers** without checking ranges and defaults (0-2 vs 0-1, whether top_k
   is available or not, whether penalties are available or not).
7. **Using penalties to fix loops that are actually a bad prompt** (e.g.
   asking for an "exhaustive list" without a stopping criterion).

---

## 9. For Further Reading

- **Holtzman et al. (2019), *The Curious Case of Neural Text Degeneration*** — the paper
  on nucleus sampling (top_p): https://arxiv.org/abs/1904.09751
- **Current model and parameter documentation from OpenAI**:
  https://developers.openai.com/api/docs/models
- **Anthropic API Documentation (Messages API)**:
  https://docs.anthropic.com/en/api/messages
- **OpenAI Cookbook, using logprobs**:
  https://cookbook.openai.com/examples/using_logprobs
- **Chip Huyen, *Generation configurations: temperature, top-k, top-p, and test time sampling***
   (sampling chapter from *AI Engineering*, 2025): https://huyenchip.com/2024/01/16/sampling.html
