# 01 — Base techniques: zero-shot, few-shot, chain-of-thought, and self-consistency

> Associated lab: [`../labs/01_zero_vs_few_shot.py`](../labs/01_zero_vs_few_shot.py) and [`../labs/02_chain_of_thought.py`](../labs/02_chain_of_thought.py)

## Why "techniques" for prompting exist

An autoregressive LLM generates the next token conditioned on everything that came before. The prompt is not a "question" that the model "understands": it is the **context that conditions the probability distribution** of the output. Prompting techniques are, fundamentally, systematic ways to shift that distribution toward where we are interested:

- **Zero-shot**: relying on what the model learned during pretraining and instruction tuning.
- **Few-shot (in-context learning)**: conditioning with examples within the prompt itself.
- **Chain-of-thought (CoT)**: having the model generate intermediate steps before the answer, because those intermediate tokens condition (and improve) the final response.
- **Self-consistency**: sampling multiple reasoning chains and keeping the majority answer.

The key observation of in-context learning (Brown et al., 2020, the GPT-3 paper) is that a sufficiently large model can "learn" a new task **without updating weights**, simply by seeing examples in the context. This entire topic is a consequence of that property.

---

## 1. Zero-shot

Asking for the task directly, without examples.

```text
Clasifica el siguiente ticket de soporte en una de estas categorías:
facturacion, tecnico, cuenta, ventas.

Ticket: "No consigo restablecer mi contraseña, el email de recuperación no llega."

Responde solo con la categoría.
```

**When to use it:**

- Common tasks that the model has seen extensively during training: summarization, translation, sentiment classification, simple extraction.
- When the cost per token matters (few-shot examples are paid for in **every** call).
- As a **baseline**: never optimize a prompt without first measuring the zero-shot performance.

**When NOT to use:**

- When the output format is idiosyncratic (your internal taxonomy of labels, a JSON with specific fields): the model cannot guess your conventions.
- Tasks with ambiguous criteria where examples define the boundary ("Is a ticket that requests an invoice and reports a bug `facturacion` or `tecnico`?").
- Domains with jargon specific to your company or client.

### Well-written vs. poorly written zero-shot

| ❌ Poor | ✅ Good |
|---|---|
| `¿De qué trata este ticket? "No me llega el email..."` | Explicit instruction + closed taxonomy + output format (example above) |
| Leaves the form of the response open: the model might return a sentence, a list, or an apology | Restricts: "Respond only with the category" |

Most "zero-shot failures" seen in practice are not model limitations: they are under-specified instructions. Before jumping to few-shot, check that your zero-shot defines **task, constraints, and output format**.

---

## 2. Few-shot (in-context learning)

Include K solved examples before the real case.

```text
Clasifica tickets de soporte en: facturacion, tecnico, cuenta, ventas.

Ticket: "Me habéis cobrado dos veces la cuota de julio."
Categoría: facturacion

Ticket: "La app se cierra al abrir la pestaña de informes."
Categoría: tecnico

Ticket: "Quiero cambiar el email asociado a mi usuario."
Categoría: cuenta

Ticket: "¿Tenéis descuento para equipos de más de 50 personas?"
Categoría: ventas

Ticket: "No consigo restablecer mi contraseña, el email de recuperación no llega."
Categoría:
```

**What examples actually contribute.** Research on in-context learning (e.g., Min et al., 2022, *Rethinking the Role of Demonstrations*) shows that much of the benefit comes from examples teaching **the format, the label space, and the input distribution**, rather than new "knowledge." Practical consequence: examples with impeccable formatting and well-balanced labels matter more than having many examples.

**Practical rules:**

1. **3–8 examples** is usually the sweet spot; beyond that, performance gains diminish while costs increase linearly.
2. **Cover all classes** and at least one boundary case (the type of input you know causes confusion).
3. **Identical format** between examples and the real case: same delimiter, same label, same capitalization. The model mimics the literal pattern.
4. **Beware of order**: models have a recency bias (they tend to favor the label of the last examples, "recency bias"; Zhao et al., 2021, *Calibrate Before Use*). Mix the classes; do not put all `facturacion` together.
5. **Correct examples**: a mislabeled example in the prompt does more damage than a 5% error rate in a fine-tuning dataset, because the model mimics it directly.

**When NOT to use few-shot:**

- Long reasoning tasks: examples consume context and do not teach reasoning (for that, use CoT).
- When examples can **anchor** too heavily: in creative generation, the model clones the style of the examples.
- With strict structured outputs (topic 04): if the schema already enforces the format, format examples are redundant; save the token budget.
- Sensitive data: examples are included in every request; do not use real customer PII as examples.

---

## 3. Chain-of-thought (CoT)

Have the model generate intermediate reasoning before the answer. Formalized by **Wei et al., 2022** (*Chain-of-Thought Prompting Elicits Reasoning in Large Language Models*): adding reasoning chains to few-shot examples substantially improves arithmetic, commonsense, and symbolic tasks — and the effect **emerges with the scale** of the model (in small models, it can even worsen performance).

Two variants:

### CoT few-shot (from Wei's paper)

The examples include the reasoning:

```text
P: Roger tiene 5 pelotas de tenis. Compra 2 botes con 3 pelotas cada uno.
   ¿Cuántas pelotas tiene ahora?
R: Roger empezó con 5 pelotas. 2 botes de 3 pelotas son 6 pelotas.
   5 + 6 = 11. La respuesta es 11.

P: <caso real>
R:
```

### CoT zero-shot

Kojima et al., 2022 (*Large Language Models are Zero-Shot Reasoners*) demonstrated that it is sufficient to add an instruction like "let's think step by step" to obtain most of the benefit without examples.

```text
<caso real>

Razona paso a paso dentro de <razonamiento>...</razonamiento> y después
escribe la respuesta final dentro de <respuesta>...</respuesta>.
```

Separating reasoning and response with tags (or asking for the final answer on the last line) is essential in production: it allows you to **parse the response without fragile regex** and discard the reasoning.

**When to use CoT:**

- Arithmetic, logic, multi-step planning, case analysis with conditions (contracts, policies, business rules).
- When you want to be able to **audit** why the model responded as it did.

**When NOT to:**

- Direct retrieval or trivial classification tasks: adds latency and cost without improving (and sometimes the model "over-reasons" and convinces itself of an error).
- When you need minimal latency: CoT multiplies output tokens, which are the expensive ones.
- **With native reasoning models** (GPT-5.6 with configurable effort and Claude's extended
  thinking): they already generate internal reasoning; asking them to reveal a private chain
  is unnecessary and fragile. Ask for a verifiable answer, evidence, and brief checks. For volume, evaluate `gpt-5.6-luna` and `claude-haiku-4-5` against your cases.

**Common error:** asking for CoT while also saying "respond only with the category". These are contradictory instructions; the model will obey one or the other in an unstable manner. If you want both, ask for reasoning in one section and the answer in another, and parse the answer section.

**Reasoning honesty warning:** the generated chain is a *verbalization*, not a faithful trace of internal computation. There is evidence (e.g., Turpin et al., 2023, *Language Models Don't Always Say What They Think*) that models can provide plausible reasoning that does not reflect the actual cause of their response. Useful for improving accuracy and for human review; do not treat it as formal proof.

---

## 4. Self-consistency

**Wang et al., 2022** (*Self-Consistency Improves Chain of Thought Reasoning in Language Models*): instead of a single reasoning chain with greedy decoding, **N chains are sampled with temperature > 0** and the final answer is chosen **by majority vote**. The intuition: there are many valid reasoning paths to the correct answer, but errors tend to disperse across different responses.

```
                     ┌─ cadena 1 → "11"
prompt CoT ── T=0.8 ─┼─ cadena 2 → "11"     → mayoría: "11"
                     ├─ cadena 3 → "12"
                     └─ cadena 4 → "11"
```

Minimal implementation (lab 02 builds it fully):

```python
from collections import Counter

answers = []
for _ in range(5):
    response = call_llm(cot_prompt, temperature=0.8)
    answers.append(extract_final_answer(response))
majority = Counter(answers).most_common(1)[0][0]
```

**Design decisions:**

- **N between 5 and 20** in the original paper; in practice N=5 already captures most of the improvement. Cost scales linearly with N: self-consistency is the most expensive technique in this topic.
- You need a **parseable final response** (number, label, option) to be able to vote. In free generation there is no trivial "majority" — the alternative there is to generate N candidates and select with a judge (topic 05).
- Temperature between 0.5 and 1.0: with temperature 0 all chains are nearly identical and voting adds no value.

**When to use it:** discrete high-value decisions where errors are costly (risk classification, critical extraction, agent gates). **When NOT to use it:** high-volume endpoints — multiplying cost by 5–10 per request is rarely justified; first exhaust prompt + better model options.

---

## How to decide: practical tree

```
¿La tarea es común y el formato simple?
 └─ Sí → zero-shot bien especificado. Mide. ¿Suficiente? Fin.
     └─ No suficiente →
        ¿El fallo es de formato/criterio de etiquetado?
         └─ Sí → few-shot (3-8 ejemplos, casos frontera incluidos)
        ¿El fallo es de razonamiento en varios pasos?
         └─ Sí → CoT (zero-shot primero; few-shot CoT si persiste)
            ¿Sigue fallando y el caso justifica ×N de coste?
             └─ Sí → self-consistency (N=5)
                ¿Sigue fallando?
                 └─ Modelo más capaz, descomponer la tarea, o fine-tuning
```

Two cross-cutting rules:

1. **Measure each step.** Without a test dataset (topic 05) this tree is astrology. The difference between "it seems to me that few-shot works better" and "few-shot increases accuracy from 0.78 to 0.91 on my dataset" is the difference between opining and engineering.
2. **Techniques compose.** Few-shot + CoT + self-consistency is exactly the recipe from Wang's paper. But each layer adds cost: add layers only when the metric justifies it.

## Common errors in this topic

1. **Jumping to the technique before specifying the task.** 80% of improvements come from clarifying instruction, taxonomy, and format.
2. **Few-shot with unbalanced examples** → the model over-predicts the most represented class.
3. **CoT without separating the final response** → fragile parsing in production.
4. **Comparing techniques with a single run and temperature > 0** → you are measuring sampling noise, not the technique.
5. **Copying prompts from another model without re-evaluating** → techniques interact with the
   specific model; a prompt tuned for one family or snapshot is not automatically
   optimal in Claude nor in the next version from the same provider.

## To go deeper

- Wei, J. et al. (2022). *Chain-of-Thought Prompting Elicits Reasoning in Large Language Models*. arXiv:2201.11903.
- Wang, X. et al. (2022). *Self-Consistency Improves Chain of Thought Reasoning in Language Models*. arXiv:2203.11171.
- Kojima, T. et al. (2022). *Large Language Models are Zero-Shot Reasoners*. arXiv:2205.11916.
- Brown, T. et al. (2020). *Language Models are Few-Shot Learners* (GPT-3). arXiv:2005.14165.
- Min, S. et al. (2022). *Rethinking the Role of Demonstrations*. arXiv:2202.12837.
- Zhao, Z. et al. (2021). *Calibrate Before Use: Improving Few-Shot Performance of Language Models*. arXiv:2102.09690.
- Anthropic's official prompting guide: https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview
- OpenAI's official prompting guide: https://platform.openai.com/docs/guides/prompt-engineering
- The Prompt Report (Schulhoff et al., 2024, 58-technique taxonomy): arXiv:2406.06608.
