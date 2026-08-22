# Domain 4 Guide — Guidelines for Responsible AI (~14% of the exam)

> Conceptual domain: dimensions of responsible AI, bias/fairness, explainability, human oversight, and associated AWS tools (Bedrock Guardrails, SageMaker Clarify, Model Cards, A2I). Fewer services, more judgment.

## 1. Dimensions of Responsible AI

The ones AWS lists (it is advisable to recognize all of them):

- **Fairness**: equitable outcomes across demographic groups; no discrimination.
- **Explainability**: the ability to explain **why** the model produced a specific output.
- **Transparency**: open information about what the model does, its data, capabilities, and limits (model cards).
- **Privacy & security**: protecting personal and customer data throughout the entire lifecycle.
- **Robustness**: functioning reliably against unexpected inputs or adversarial attacks.
- **Governance**: policies, processes, and auditing over the AI lifecycle.
- **Veracity / safety**: truthful and non-harmful outputs; controlling hallucinations and toxic content.
- **Controllability**: the ability to direct and limit the system's behavior.
- **Human-centricity / accountability**: humans are responsible and in the loop where it matters.

## 2. Bias (bias): types and mitigation

- **Origin of bias**: almost always **the training data** (unrepresentative samples, historical prejudices, biased labels), as well as feature decisions and the feedback loop itself.
- Types that appear on the exam: **sampling/selection bias** (unrepresentative sample), **measurement bias** (systematically skewed measurements), **historical bias** (data reflecting past discrimination), **confirmation bias** (human), **algorithmic bias** (amplified by the model).
- **Fairness metrics**: comparing outcomes between subgroups (e.g., disparate impact, difference in approval rates).
- Mitigation: **diverse and representative** datasets, audits with **SageMaker Clarify** (pre- and post-training), data rebalancing, continuous monitoring in production, human review in sensitive decisions (credit, hiring, health).
- **Bias-variance** ≠ social bias: do not confuse statistical bias (underfitting) with fairness bias. The exam may play on this word.

## 3. Explainability, transparency, and interpretability

- **Interpretable model**: understood by construction (linear regression, decision trees).
- **Explainable (post-hoc)**: opaque model + techniques that explain its outputs (**SHAP**, feature importance) — this is what **SageMaker Clarify** does.
- Classic tradeoff: **more powerful models (deep learning, FMs) are less interpretable**; if the scenario requires justifying every decision (regulator, credit), the answer may be an interpretable model even if it performs slightly less.
- **Documentary transparency**:
  - **SageMaker Model Cards**: standardized model documentation (intended use, data, metrics, limitations, ethical considerations).
  - **AWS AI Service Cards**: the same but published by AWS for **its** AI services (Rekognition, Textract...).

## 4. Responsible datasets and human oversight

- Data: **representativeness**, quality, consent and license, PII minimization, continuous curation (data curation), documented provenance.
- **Human-in-the-loop (HITL)**: human review of predictions — in AWS, **Amazon A2I** (review workflows for low-confidence predictions or random sampling).
- **SageMaker Ground Truth**: humans for **labeling** training data (do not confuse with A2I, which reviews **inferences**).
- High-impact decisions (medical, legal, financial) → the exam expects **human oversight**, never total automation.

## 5. Specific risks of generative AI

- **Hallucinations**: mitigate with RAG/grounding, Guardrails (contextual grounding check), human review, and communicating limits to the user.
- **Toxicity / harmful content**: content filters (Guardrails), moderation.
- **PII and privacy**: do not send unnecessary sensitive data; PII redaction.
- **IP/copyright and plagiarism**: generated content may resemble protected material.
- **Misuse**: deepfakes, disinformation, fraud.
- **Prompt injection/jailbreak** (crosses with domains 3 and 5).
- **Legal/reputational**: liability for incorrect outputs; loss of customer trust.

## 6. Amazon Bedrock Guardrails (star of the domain)

Configurable security layer **independent of the model** (applies to any Bedrock FM, Agents, and Knowledge Bases). Capabilities:

- **Content filters**: thresholds for hate, insults, sexual, violence, misconduct, and **prompt attacks** (in input and output).
- **Denied topics**: banned topics defined in natural language (e.g., "investment advice").
- **Word filters**: blocked words/phrases (competitors, profanities).
- **Sensitive information filters**: detect and **block or mask PII** (custom regex included).
- **Contextual grounding checks**: verify that the response is grounded in the source (anti-hallucination in RAG).
- Note: Guardrails **filters/controls content at runtime**; it does not retrain or "fix" the model.

## 7. Other AWS tools in the domain

- **SageMaker Clarify**: **bias detection** (before and after training) + **explainability** (SHAP) + evaluation of FMs.
- **SageMaker Model Monitor**: monitors **drift** in data/model quality in production (responsible quality is sustained over time).
- **Amazon A2I**: human review of predictions.
- **Model Cards / AI Service Cards**: documentary transparency.

## 8. Typical exam traps

- **Guardrails vs Clarify**: filtering content/PII/topics in a chatbot **at runtime** → **Guardrails**; analyzing **dataset/model bias** or explaining predictions → **Clarify**.
- **Ground Truth vs A2I**: labeling data for training → Ground Truth; reviewing predictions in production → A2I.
- **Model Cards vs AI Service Cards**: you document YOUR model → Model Cards; AWS documentation about THEIR services → AI Service Cards.
- **Model Monitor vs Clarify**: drift in production → Model Monitor; bias/explainability → Clarify (Clarify can also monitor bias drift via Model Monitor, but in the exam the word "drift" points to Model Monitor).
- **"The model discriminates against a group" →** review/rebalance **the training data** and measure with Clarify; "adding more layers to the network" is a distractor.
- **Interpretability**: if they ask to "be able to explain every decision to a regulator" → interpretable model (tree/linear) or SHAP/Clarify; not "using a larger FM".
- **Hallucinations**: mitigation = grounding/RAG + contextual grounding check + human review; **not** "increasing temperature" nor "expanding context window".
- **Fairness ≠ accuracy**: a model can be very accurate and still unfair to a subgroup.
- **Total automation** in sensitive decisions is almost never the correct option: look for the answer with human oversight.

## 9. Review mini-scenarios (exam format)

- *"The banking chatbot must not discuss investment advice."* → Guardrails with denied topics.
- *"Emails and phone numbers must be masked in the bot's responses."* → Guardrails with sensitive information filters (PII).
- *"The credit model approves fewer applications from a specific group."* → Measure bias with SageMaker Clarify and rebalance the training data.
- *"The regulator requires explaining why each application was denied."* → Explainability: SHAP with Clarify, or directly an interpretable model.
- *"Document intended use, metrics, and limitations of our model."* → SageMaker Model Cards.
- *"Know the limitations AWS declares for Rekognition."* → AWS AI Service Cards.
- *"Medical model diagnoses must be reviewed by a doctor before being communicated."* → Human-in-the-loop with Amazon A2I.
- *"Model quality drops because production data has changed."* → SageMaker Model Monitor (drift).
- *"The RAG assistant answers things that are not in the documents."* → Contextual grounding check of Guardrails (+ retrieval review).
- *"Choose between a deep model with 95% accuracy and a tree with 91% for auditable decisions."* → The interpretable one, if the requirement is to explain decisions.

## 10. Quick glossary

| Term | Exam Definition |
|---|---|
| Fairness | Equitable outcomes between groups |
| Bias (social) | Systematic discrimination inherited from data |
| Sampling bias | Non-representative training sample |
| Fairness metric | Measure comparing outcomes between subgroups |
| Explainability | Explaining why the model gave an output (post-hoc) |
| Interpretability | The model is understandable by construction |
| SHAP | Feature attribution technique to explain predictions |
| Transparency | Documenting what the model does, with what data, and limits |
| Model Card | Standardized documentation sheet for a model |
| HITL | Human-in-the-loop: human review of outputs |
| Toxicity | Harmful/offensive generated content |
| Contextual grounding | Verifying that the response is supported by the source |
| Denied topic | Topic vetted/configured in Guardrails |
| Veracity | Factual accuracy of outputs |
| Accountability | Human responsibility assigned to the system |

## 11. Pre-exam checklist

- [ ] I list the dimensions of Responsible AI (fairness, explainability, transparency, privacy, robustness, governance, safety, controllability).
- [ ] I explain where bias comes from and how it is mitigated (representative data + Clarify + monitoring).
- [ ] I distinguish interpretable (by construction) from explainable (post-hoc, SHAP).
- [ ] I distinguish Guardrails (runtime) / Clarify (bias+explainability) / Model Monitor (drift) / A2I (human review).
- [ ] I distinguish Model Cards (my model) from AI Service Cards (AWS services).
- [ ] I list the 5 capabilities of Bedrock Guardrails.
- [ ] I know that high-impact decisions require human oversight.
- [ ] I identify the genAI risks: hallucinations, toxicity, PII, IP, misuse, prompt attacks.
- [ ] I remember that fairness ≠ accuracy and that statistical bias ≠ social bias.

## 12. How to read questions in this domain

- If the scenario mentions an **adversely affected demographic group**, the answer revolves around representative data + Clarify, not changing the algorithm.
- If it mentions **regulator/audit/justifying decisions**, look for explainability (SHAP/Clarify) or an interpretable model.
- If it mentions **inappropriate content/PII/prohibited topics in a chatbot**, the answer is Guardrails.
- If it mentions **automated medical/financial/legal decisions**, the answer includes human review (A2I).
- If it mentions **documenting the model**, it is Model Cards; if it is AWS documentation about their services, AI Service Cards.
- The option "do nothing because the model is accurate" or "automate everything" is almost always incorrect in this domain.
- When in doubt between two controls, choose the one that acts **closer to the origin of the problem** (data → training → runtime → human review).

## Mapping to the repo

This domain corresponds to **module 5 (Responsible AI, guardrails, safety in production)**, with support from module 2 (bias and hallucination detection).

## Resources for further study

- AWS Responsible AI (official page and published AI Service Cards).
- Amazon Bedrock Guardrails documentation (capabilities and configuration).
- SageMaker Clarify documentation (bias metrics and SHAP).
- AWS whitepaper/blog on Responsible Use of Machine Learning.
- AWS Skill Builder course: Responsible AI Practices (free).
- NIST AI Risk Management Framework (light reading: executive summary is sufficient).

---

> ⚠️ **Note**: The content, weights, and services mentioned are subject to change. Always verify the official **AIF-C01 Exam Guide** at aws.amazon.com/certification before taking the exam.
