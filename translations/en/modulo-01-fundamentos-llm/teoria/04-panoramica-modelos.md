# Current Landscape: GPT-5.6, Claude 5, Gemini 3.x, Llama 4, and Mistral

> **Module 1 · Topic 4** · Estimated study time: 2 h
> Associated labs: `labs/01_primer_llamada_openai.py`, `labs/02_primer_llamada_anthropic.py`
> Associated exercises: 5, 6, 7, and 10.

> ⚠️ **Expiration.** This is the module topic that ages the fastest. The specific names and
> capabilities described here are a snapshot from **August 21, 2026**; what you should
> retain is not the snapshot, but the **family map** and the **method for evaluating**
> any new model that emerges (section 6).

---

## 1. How to Read the Market: The Three Axes

To avoid getting lost among dozens of names, position each model along three axes:

1. **Access**: Closed weights behind an API (GPT, Claude, Gemini) or open weights that
   you can download and serve yourself (Llama, Mistral, Qwen, DeepSeek)? "Open weights" does
   not always mean open source: read the license (Llama's has commercial clauses;
   Mistral publishes some models under Apache 2.0).
2. **Size/tier**: Each provider maintains a ladder — a flagship model (expensive,
   maximum capability), an intermediate one, and a small/cheap one for high-volume tasks.
   Learning the ladder matters more than learning the names: *most production tasks work well with the small or medium tier*.
3. **Inference regime**: "Classic" models (respond directly) vs models with
    **configurable reasoning** (GPT-5.6, Claude's adaptive thinking, Gemini thinking
   and open reasoning models). You do not need to, nor should you rely on, the private chain:
   evaluate the response, its evidence, and the use of tools. More reasoning may
   improve math/code/planning at the cost of latency and expense.

---

## 2. Proprietary Families

### OpenAI: GPT-5.6

- The current family is **GPT-5.6**, featuring configurable reasoning effort and three
  explicit profiles: **Luna** for cost-sensitive volume, **Terra** as the balance,
  and **Sol** for maximum capability. Labs use `gpt-5.6-luna`; each project should
  promote to another tier only if its evaluation justifies it.
- The recommended API for new integrations is **Responses**: it unifies typed outputs,
  tools, and continuity. Chat Completions remains useful for maintaining legacy systems,
  but it is not the starting point of the course.
- The 5.6 generation adds capabilities that change agent architecture: **persisted
  reasoning** to continue work across turns, **Programmatic Tool Calling (PTC)** to
  orchestrate tools from generated code, `pro` reasoning mode for the most
  difficult cases, and `safety_identifier` to associate abuse with a user without sending
  personal data. Not all tasks require these features: they are activated only when an evaluation
  demonstrates that they justify their cost and latency.
- GPT-4o and the o-series were important historical steps toward multimodality and
  commercial reasoning. They are preserved in historical chapters and encoding names,
  not as operational defaults.

### Anthropic: Claude

- The August 2026 catalog offers **Claude Fable 5** as the top capacity for
  long-running agent execution, **Claude Opus 5** for complex agentic code and
  enterprise work, and **Claude Sonnet 5** as the balanced option; **Claude Haiku 4.5** remains
  the active fast tier.
- In Claude 5, modern control is **adaptive thinking**: the model dynamically decides
  how much to reason based on the problem and the configured effort. Do not confuse this with
  the manual *extended thinking* of previous generations, which remains available in Haiku
  4.5 but is not the mechanism for Sonnet 5. Always check the compatibility matrix of
  the snapshot you are going to use.
- Other key identifiers: long contexts, code and tool/agent usage, and
  emphasis on safety/steerability. Own API (`messages`), also available via
  Bedrock and Vertex.
- In the labs we use `claude-haiku-4-5`. In production, fix the snapshot with a date when
  it is available and run the evaluation before migrating it.

### Google: Gemini

- In August 2026, **Gemini 3.7 Flash** is the recommended stable workhorse and **Gemini
  3.6 Flash** is the previous stable generation. **Gemini 3.5 Flash** remains available as
  a stable legacy and **Gemini 3.5 Flash-Lite** covers cost-sensitive volume; **Gemini 3.1
  Pro** appears as a preview. This distinction matters: a preview is for evaluation, not
  for entering production by inertia. Gemini 1.5/2.x were historical milestones in
  massive context, multimodality, and integrated thinking.
- Strengths: enormous context, integration with the Google ecosystem (Workspace, Vertex
  AI), and very competitive Flash tiers in price. Google's open models are called
  **Gemma**.

---

## 3. The open families

### Meta: Llama

- **Llama 4 Scout and Maverick** remain the current downloadable open-weight line from
  Meta in this overview and moved the family to a multimodal Mixture-of-Experts. Meta also
  offers **Muse Spark** in its own products since 2026, but it is not a new downloadable
  version of Llama: do not present it as an on-premise substitute. Llama 3.x remains
  widely deployed and is useful for understanding the transition, but should not be assumed
  as the best new option.
- Its importance is ecosystemic: most local tooling (llama.cpp, Ollama,
  vLLM, cheap fine-tuning) grew around Llama, and its license — although not pure OSS
  — allowed companies to deploy on their own infrastructure.

### Mistral

- European startup (France). The general August 2026 catalog is structured around
  **Mistral Medium 3.5**, **Mistral Small 4** and **Mistral Large 3**, in addition to
  specialized models for code, reasoning, OCR, and audio. Mistral 7B and Mixtral 8x7B are
  historical milestones, not the automatic recommendation for a new deployment.
- Relevant if you care about: European data sovereignty, on-premise deployment, and
  very efficient small models.

### The rest of the open pack (don't ignore it)

**Qwen** (Alibaba) maintains Qwen3 as the open generation and an API line 3.x that already
includes Qwen 3.6; **DeepSeek** (whose R1, January 2025, demonstrated frontier reasoning
with open weights and modest training cost) competes head-to-head with Llama. If
you work with local models in 2026, it is most likely that you will end up testing Qwen or
DeepSeek first. Check the exact snapshot and license: these catalogs do
not update at the same pace as closed generations.

---

## 4. Summary table (snapshot as of August 21, 2026)

| Provider | Family | Typical Tiers | Access | Differentiating Feature |
|---|---|---|---|---|
| OpenAI | GPT-5.6 Luna / Terra / Sol | volume ↔ flagship | API | Configurable responses, tools, and reasoning |
| Anthropic | Claude Haiku 4.5 / Sonnet 5 / Opus 5 / Fable 5 | fast ↔ long agents | API (+Bedrock/Vertex) | Code, agents, long context, adaptive thinking |
| Google | Gemini 3.5–3.7 Flash / 3.1 Pro preview | Flash-Lite ↔ Pro | API (+Vertex) | Long context and multimodality |
| Meta | Llama 4 | sizes/MoE per variant | Open weights | Local ecosystem and self-hosted deployment |
| Mistral | Medium 3.5 / Small 4 / Large 3 | Small ↔ Large | Hybrid | Efficiency, deployment, and European sovereignty |
| Alibaba | Qwen 3.x | multiple sizes | Open weights/API | Multilingual, code, and broad range |
| DeepSeek | V/R catalog current | per variant | Open weights/API | Reasoning and efficient deployment |

---

## 5. Practical selection criteria

Questions in order, from most eliminatory to least:

1. **Data/deployment constraints?** If data cannot leave your infrastructure →
   open weights (or API in your cloud via Bedrock/Vertex/Azure). This eliminates half of
   the table at a glance.
2. **What does the task require?** Context (do your documents fit?), modalities (image?
   audio?), language (real performance in Spanish), tools (function calling,
   structured output), deep reasoning or speed?
3. **What latency and cost does the product tolerate?** A support chatbot with thousands of
   conversations/day lives in the small tier; a one-off legal analysis can
   afford the flagship tier with reasoning. Prices: always check the provider's official
   pricing page (they change several times a year; any figure written here
   would be outdated within months).
4. **What does YOUR eval say?** The only definitive answer (section 6).

Very common architecture pattern: **difficulty-based routing** — the cheap tier handles
90% of requests and scales to the large model only for difficult cases.

---

## 6. How to evaluate a new model (the method that doesn't expire)

Every few months, "the best model in history" will emerge. Protocol:

1. **Be skeptical of classic benchmarks.** MMLU, HumanEval, and the like are saturated
   and contaminated (their data ends up in training corpora). Differences of 1-2
   points mean nothing.
2. **Look at live comparisons** with their limitations: LMArena (blind human
   preferences; measures "liking", not "correctness"), code leaderboards like SWE-bench, Artificial
   Analysis for quality/cost/latency ratios.
3. **Build your mini-eval.** 20-50 real cases from *your* application with defined
correctness criteria. Run it against the new model and the current one. Half an hour of work
   that is worth more than any press release. (In the evaluation module of the program
   this is systematized; you already know the rule from the benchmarking lab: publish
   only from the serious harness.)
4. **Measure non-functional aspects**: p95 latency, error/refusal rate, stability of
   output format, real cost per request with *your* prompts (remember from topic 2:
   token counts differ between tokenizers).
5. **Pin versions in production.** `model="...-latest"` or floating aliases = your app
   changes behavior without warning. Use date-stamped snapshots and migrate deliberately.

---

## 7. Common Mistakes

1. **Choosing a model based on headlines or a single benchmark.** The question is not "which is the best?" but "which is the cheapest that meets my quality threshold?".
2. **Using the flagship model for everything.** Paying significantly more for tasks that the smaller tier handles just as well is the most common cost error in production.
3. **Ignoring reasoning models... or overusing them.** For complex logic, they are in a different league; for extracting a field from an email, they are a waste of latency and money.
4. **Assuming "open weights" = free.** Serving a 70B model with good latency requires GPU, engineering, and operations; at low volume, the API is almost always cheaper.
5. **Not reviewing the license** of open models before commercial use.
6. **Treating `-latest` aliases as stable versions** in production.
7. **Evaluating in English and deploying in Spanish** without checking for degradation.

---

## 8. For Further Reading

- **Model sheets and official documentation**:
  OpenAI: https://developers.openai.com/api/docs/models ·
  Anthropic: https://platform.claude.com/docs/en/about-claude/models/overview ·
  Gemini: https://ai.google.dev/gemini-api/docs/models ·
  Llama/Meta: https://ai.meta.com/llama/get-started/ ·
  Qwen: https://qwenlm.github.io/qwen-code-docs/en/users/configuration/model-providers/ ·
  Mistral: https://docs.mistral.ai/models
- **LMArena (formerly LMSYS Chatbot Arena)** — human preference ranking:
  https://lmarena.ai/
- **Artificial Analysis** — quality/cost/latency comparisons between APIs:
  https://artificialanalysis.ai/
- **SWE-bench** — code evaluation on real GitHub issues:
  https://www.swebench.com/
- **DeepSeek-R1 (2025)** — paper on open reasoning with RL:
  https://arxiv.org/abs/2501.12948
