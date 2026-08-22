# 07 — Responsible AI: From Principles to Measurable Controls

Responsible AI is not a values page or a filter at the end. It is a process to identify
who can suffer harm, translate that into verifiable requirements, and maintain evidence throughout the entire
lifecycle.

## 1. From Principle to Control

| Principle | Operational Question | Evidence |
|---|---|---|
| Fairness | Which groups receive different outcomes and why? | Segmented metrics, counterfactual pairs |
| Transparency | Does the user know they are interacting with AI and its limits? | UI, model/system card |
| Explainability | Can we justify the data, rules, and sources? | Citations, features, traces, reason codes |
| Privacy | What data enters, is stored, and is shared? | Inventory, DPIA, retention, deletion |
| Security | How is abuse or data extraction prevented? | Threat model, red-team, incidents |
| Robustness | What happens out-of-distribution or when tools fail? | Evals, fault injection, SLOs |
| Accountability | Who approves, monitors, and responds? | RACI, gates, runbooks, logs |

A principle without an owner, metric, and gate does not change engineering decisions.

## 2. Classify the Case by Impact

Before the model, document:

- Affected users and non-users;
- Decisions it informs or automates;
- Reversibility and severity of error;
- Vulnerable populations and unanticipated use contexts;
- Data sources and jurisdictions;
- Human dependency and the real possibility of appeal;
- Abuse threats.

The greater the impact, the stricter the evidence, supervision, and limits must be. An internal copy generator and a system prioritizing help requests do not share the same threshold.

## 3. Human-in-the-Loop That Actually Means Something

Adding an "approve" button does not reduce risk if the human:

- Receives hundreds of cases per hour;
- Cannot see sources or uncertainty;
- Believes the model is almost always correct;
- Is penalized for disagreeing;
- Cannot edit or revert;
- Lacks training or authority.

Design the review with information, time, reason codes, sources, editing, and escalation channel.
Measure override rate, override accuracy, time, and disagreement. If no one ever rejects, it may be
high quality or complacent automation: investigate.

## 4. Fairness in generative systems

Define groups and relevant outcome. For classification with ground truth you can measure:

```text
TPR_g = verdaderos_positivos_g / positivos_reales_g
FPR_g = falsos_positivos_g / negativos_reales_g
gap_TPR = max(TPR_g) - min(TPR_g)
```

For generation, evaluate properties such as toxicity, stereotypes, quality, rejection, factualness, and
utility per segment. Use counterfactual pairs where only the attribute changes, plus natural cases
that represent dialects and real situations.

Precautions:

- small sample sizes produce unstable gaps;
- an average can hide intersections;
- removing a sensitive column does not eliminate proxies;
- different fairness metrics may be incompatible;
- measuring a sensitive attribute requires legal basis, minimization, and controls.

The fair definition belongs to the product context and must involve experts and affected parties.

## 5. Transparency and explainability

The appropriate explanation depends on the consumer:

- **user:** what the system does, what data it used, limitations, and how to correct/appeal;
- **operations:** trace, sources, version, and events;
- **auditor:** controls, dataset, results, and changes;
- **engineering:** signals per component and reproduction.

Do not present the generated chain-of-thought as a causal explanation. It may be rationalization.
Prefer verifiable evidence: applied rules, tool calls, citations, and external decision factors.

## 6. Model card and system card

A minimal card:

```markdown
# Sistema: NebulaOps Support Assistant

## Propósito y fuera de alcance
- Ayuda a localizar documentación interna de soporte.
- No ejecuta cambios de infraestructura ni da asesoramiento legal.

## Componentes y versiones
- Modelo/política de routing
- Corpus e índice
- Prompts, tools y guardrails

## Datos
- Fuentes, licencias, actualización, PII y retención

## Evaluación
- Dataset, segmentos, métricas, intervalos y fallos conocidos

## Riesgos y mitigaciones
- Alucinación, sesgo, inyección, acceso cruzado y abuso

## Operación
- Propietario, alertas, rollback, feedback y contacto
```

Update it with every material change; a static launch card becomes false.

## 7. Privacy by design

Data map by stage:

```text
entrada → logs/trazas → proveedor → retrieval/store → feedback/eval → backups → borrado
```

For each arrow, specify purpose, legal basis, region, access, retention, and deletion. Controls:

- minimization and redaction before logging;
- separation of payload and metadata;
- no-retention options and provider contracts where applicable;
- encryption and audited access;
- anonymized evaluation datasets;
- deletion propagated to indexes, caches, and backups according to policy;
- do not reuse conversations for training without explicit decision.

## 8. Human evaluation

Design an annotation guide with edge-case examples. Use at least two annotators on a sample and
measure agreement. Disagreement reveals policy or task ambiguity; do not hide it by taking an average.

Protect annotators from harmful content, inform them about the task, and avoid collecting irrelevant
personal attributes. Responsible AI also applies to the evaluation process.

## 9. Relevant AWS Tools

- **Amazon Bedrock Guardrails:** configurable policies for inputs/outputs; measure false positives and negatives against your domain.
- **Bedrock model evaluation:** automatic or human evaluation based on current capabilities.
- **SageMaker Clarify:** bias analysis and explainability for compatible ML workflows.
- **SageMaker Model Cards:** documentation and lifecycle governance.
- **Amazon Macie:** sensitive data discovery in S3, not a universal semantic filter.
- **CloudTrail/Config/Audit Manager:** activity, configuration, and compliance evidence.

No service decides what is fair for your product. Provide mechanisms, not the definition.

## 10. Monitoring and Change

Online signals:

- quality by segment and opt-out rate;
- complaints, overrides, and appeals;
- toxicity/rejection by language;
- input and corpus drift;
- invalid citations and access denied;
- incidents and near misses;
- cost/latency that pushes users to shortcuts.

Define re-evaluation triggers: new model, prompt, corpus, tool, market, language, or policy.

## 11. Lightweight but Real Governance

For a small team, a versioned registry is sufficient:

| Field | Example |
|---|---|
| system/owner | support-assistant / AI team |
| impact level | medium |
| permitted uses | search and drafting |
| prohibited uses | automatic decision-making regarding people |
| mandatory evaluations | quality, PII, injection, fairness by language |
| approvers | product, security, domain |
| next review | date or trigger |
| rollback | previous alias/model/index |

Documentation must reflect decisions, not produce uncontrolled bureaucracy.

## Common Errors

1. Treating Responsible AI as synonymous with moderation.
2. Measuring fairness without defining the outcome or harm.
3. Calling human-in-the-loop a de facto automatic approval.
4. Saving all traces "just in case".
5. Presenting model-generated text as a reliable explanation.
6. Failing to reevaluate after changing the corpus or model.
7. Delegating responsibility to the cloud provider.

## For Further Reading

- NIST AI RMF: https://www.nist.gov/itl/ai-risk-management-framework
- OECD AI Principles: https://oecd.ai/en/ai-principles
- AWS Responsible AI: https://aws.amazon.com/machine-learning/responsible-ai/
- Model Cards: https://arxiv.org/abs/1810.03993
- Datasheets for Datasets: https://arxiv.org/abs/1803.09010
