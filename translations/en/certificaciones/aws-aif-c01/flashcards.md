# AWS Certified AI Practitioner (AIF-C01) Flashcards

> Flashcards grouped by the 5 domains of revision 1.1. Question → Answer format: cover the answer, answer aloud, and check. Weights and syllabus may change: verify the **official exam guide** before taking the exam.

---

## Domain 1 — Fundamentals of AI and ML

**Q:** What is the relationship between AI, ML, and deep learning?
**A:** Deep learning ⊂ machine learning ⊂ artificial intelligence. DL uses deep neural networks; ML learns patterns from data; AI is the broader field.

**Q:** What distinguishes supervised learning from unsupervised learning?
**A:** Supervised training uses **labeled** data (classification, regression); unsupervised finds structure in **unlabeled** data (clustering, dimensionality reduction).

**Q:** What is reinforcement learning?
**A:** An agent learns through trial and error by interacting with an environment and maximizing a reward signal. It does not use a labeled dataset.

**Q:** Classification vs. regression?
**A:** Classification predicts a **category** (spam/not spam); regression predicts a **continuous value** (price, demand).

**Q:** What is overfitting and how is it mitigated?
**A:** The model memorizes the training data and generalizes poorly (high train accuracy, low test accuracy). Mitigation: more data, regularization, simpler models, early stopping.

**Q:** Why is accuracy misleading with imbalanced classes and what metrics should be used?
**A:** A model that always predicts the majority class "gets it right" almost all the time. Use precision, recall, and F1; use recall if false negatives are costly (fraud, disease).

**Q:** Precision vs. recall?
**A:** Precision: of what was marked positive, how much was actually positive. Recall: of all actual positives, how many were captured.

**Q:** Batch inference vs. real-time inference?
**A:** Batch: periodic massive predictions, no urgency, cheaper. Real-time: always-active endpoint with immediate response, more expensive.

**Q:** What is feature engineering?
**A:** Creating/transforming input variables from raw data so the model learns better (normalization, encoding, aggregations…).

**Q:** What does Amazon Textract do?
**A:** Extracts text, tables, and key-value pairs from scanned documents (intelligent OCR). Documents, not general photos.

**Q:** What does Amazon Comprehend do?
**A:** Managed NLP on text: sentiment, entities, key phrases, language, and PII detection.

**Q:** What does Amazon Rekognition do?
**A:** Computer vision on images and video: objects, scenes, faces, text in image, and content moderation.

**Q:** Polly vs. Transcribe?
**A:** Polly: text-to-speech (TTS). Transcribe: speech-to-text (STT). They are inverses.

**Q:** What is Amazon SageMaker AI in one sentence?
**A:** The managed platform for building, training, evaluating, and deploying **your own** end-to-end ML models.

**Q:** When should you NOT use ML?
**A:** When the problem can be solved with simple, stable deterministic rules (tax calculations, validations), or when there is insufficient data.

---

## Domain 2 — Fundamentals of Generative AI

**Q:** What is a foundation model?
**A:** A large pre-trained model with massive data (usually self-supervised) that adapts to many tasks via prompting, RAG, or fine-tuning.

**Q:** What is a token and what is the context window?
**A:** The token is the minimum unit of text the model processes (~subwords). The context window is the maximum number of input+output tokens per request.

**Q:** What are embeddings?
**A:** Numerical vectors that represent the meaning of text (or images); similar texts end up close in the vector space → semantic search.

**Q:** What does temperature control?
**A:** Sampling randomness: low → more deterministic/repeatable outputs; high → more diverse/creative outputs.

**Q:** Temperature vs. top_p vs. top_k?
**A:** All three regulate sampling: temperature rescales probabilities; top_p limits to the cumulative probability nucleus; top_k limits to the k most probable tokens.

**Q:** What does max tokens control?
**A:** Only the **maximum length** of the output. It does not affect creativity or quality.

**Q:** What is a hallucination?
**A:** Invented but plausible content presented with confidence. Mitigation: RAG/grounding, low temperature, guardrails, human review.

**Q:** Order from lowest to highest cost to adapt an FM:
**A:** Prompt engineering → RAG → fine-tuning → continued pre-training → training from scratch.

**Q:** Fine-tuning vs. continued pre-training?
**A:** Fine-tuning: **labeled** data (prompt-response pairs) for task/style. Continued pre-training: **unlabeled** corpus to absorb domain language.

**Q:** Zero-shot vs. few-shot?
**A:** Zero-shot: instructions only. Few-shot: solved examples included in the prompt (in-context learning, without changing weights).

**Q:** What is Amazon Bedrock?
**A:** A serverless service providing unified API access to foundation models from Amazon and third parties (Anthropic, Meta, Mistral…), with customization, Agents, Knowledge Bases, and Guardrails.

**Q:** What is Amazon Q Business?
**A:** Managed generative AI assistant for employees: connects to corporate data (S3, SharePoint, Salesforce…) while respecting permissions. Q Developer is its sibling for code/AWS.

**Q:** What is Amazon Quick?
**A:** Managed AI workspace for chat, agents, BI/visualization, research, and automation on connected data and applications. Amazon Quick Sight is the business intelligence capability within Quick.

**Q:** What is Kiro in the AIF-C01 scope?
**A:** An agentic IDE for specification-driven development, steering files, and hooks that automate quality controls.

**Q:** What are Strands Agents?
**A:** Open-source, model-first SDK for building agents with tools, multiple providers, and protocols like MCP. It is code/framework, not managed hosting.

**Q:** What is Amazon Bedrock AgentCore?
**A:** Model- and framework-agnostic infrastructure for deploying and operating agents: Runtime, Gateway, Memory, Identity, Observability, Evaluations, and Policy.

**Q:** Strands Agents vs AgentCore?
**A:** Strands builds the agent logic; AgentCore can host and operate agents from Strands, LangGraph, CrewAI, or custom code with managed services.

**Q:** What does AgentCore Identity provide?
**A:** Workload identity and secure credential management so agents and tools can access AWS or third-party services, with authentication, authorization, and auditable tracing.

**Q:** What is model distillation?
**A:** Training a smaller model to mimic the behavior of a larger one; aims to preserve useful quality while reducing cost and latency.

**Q:** On-demand vs Provisioned Throughput in Bedrock?
**A:** On-demand: pay-per-token, variable traffic. Provisioned: reserved capacity, stable cost, and guaranteed throughput; required for serving customized models.

**Q:** Which metric is associated with summaries and which with translation?
**A:** ROUGE for summarization; BLEU for translation. Both compare against reference texts.

**Q:** What is the knowledge cutoff?
**A:** The training data deadline: the model does not know facts after this date. This is compensated with RAG or tools.

**Q:** What is a multimodal model?
**A:** One that accepts and/or generates multiple modalities (text, image, audio) in the same request.

**Q:** Prompt engineering vs context engineering?
**A:** Prompt engineering designs instructions and examples. Context engineering also composes history, memory, RAG documents, tool results, and metadata within the window and token budget.

**Q:** What does MCP bring to an agentic system?
**A:** A standard interface for discovering and using tools, resources, and context from external systems. MCP connects; orchestration decides the sequence, state, retries, and approvals.

**Q:** When does a multi-agent system make sense?
**A:** When specialization, delegation, or review between agents adds more value than their cost, latency, and complexity. For a linear task, a single agent is usually better.

---

## Domain 3 — Applications of Foundation Models

**Q:** What is RAG and when to choose it?
**A:** Retrieval-Augmented Generation: retrieve relevant chunks from your data and inject them into the prompt. Choose it when knowledge changes frequently or must be cited, without retraining.

**Q:** What does Bedrock Knowledge Bases do?
**A:** Managed RAG: ingestion from S3, chunking, embeddings, vector store (e.g., OpenSearch Serverless), and retrieve/retrieve-and-generate APIs.

**Q:** What is chunking and why does it matter?
**A:** Splitting documents before generating embeddings. Well-sized chunks → more accurate retrieval and context that fits within the model's window.

**Q:** Name two vector store options in AWS.
**A:** Guide 1.1 cites Amazon OpenSearch Service, Aurora, Neptune, and Amazon RDS for PostgreSQL; pgvector is the usual mechanism in PostgreSQL.

**Q:** What does Bedrock Agents do?
**A:** Orchestrates multi-step tasks: the model plans, calls APIs defined in **action groups**, queries knowledge bases, and returns the result.

**Q:** Knowledge Bases vs Agents: when to use each?
**A:** Only answering questions about documents → Knowledge Bases. Executing actions against APIs (creating tickets, orders) → Agents (which may include a KB).

**Q:** What is chain-of-thought prompting?
**A:** Asking for step-by-step reasoning before the final answer; improves logic and multi-step tasks.

**Q:** What does Amazon Bedrock Prompt Management do?
**A:** Allows creating, testing, saving, versioning, and reusing prompts and variants. Each version must be evaluated with a stable dataset and retain a rollback path.

**Q:** What is prompt injection and how is it mitigated?
**A:** User input that attempts to override system instructions ("ignore your instructions…"). Mitigation: guardrails, separating instructions from data, validating inputs, least privilege in tools.

**Q:** What does Bedrock Guardrails do?
**A:** Filters at inference: denied topics, harmful content, PII (blocking or masking), word filters, and contextual grounding detection. Applies to input and output.

**Q:** What is Bedrock Model Evaluation?
**A:** Comparing FMs with automatic metrics (accuracy, robustness, toxicity) or human evaluation on custom datasets, to choose a model.

**Q:** Criteria for choosing a foundation model:
**A:** Modalities, quality on the task, context window size, cost per token, latency, languages, customization options, and license.

**Q:** When to choose fine-tuning over RAG?
**A:** When you want to fix **style/format/behavior** with many labeled examples. RAG when the problem is **knowledge** that is updated or citable.

**Q:** What are stop sequences?
**A:** Strings that, when generated, stop the output. Used to delimit formats and avoid extra text.

**Q:** Prompt best practices for RAG:
**A:** Delimit the retrieved context, order "answer only with this context", ask to "say you don't know" if information is missing, and ask for citations.

**Q:** What happens to your data when customizing a model in Bedrock?
**A:** They remain private: a copy of the model is created for your account, and your data is not used to improve the base models.

**Q:** What is right-sizing inference?
**A:** Using the smallest model that meets the required quality: lower cost and latency. Do not use the largest one "just in case".

---

## Domain 4 — Guidelines for Responsible AI

**Q:** Typical dimensions of Responsible AI:
**A:** Fairness, explainability, transparency, privacy and security, robustness, governance, controllability, and veracity.

**Q:** What is fairness?
**A:** That the system does not systematically produce worse outcomes for protected groups (gender, age, ethnicity...).

**Q:** What is the most common source of bias in a model?
**A:** Biased or unrepresentative training data: the model reproduces the discrimination present in the historical data.

**Q:** What does SageMaker Clarify do?
**A:** Detects bias in data and models (pre- and post-training) and explains predictions with feature attributions (SHAP).

**Q:** Guardrails vs Clarify?
**A:** Guardrails filters content during **inference** (topics, toxicity, PII). Clarify analyzes **bias and explainability** in the ML lifecycle. They do not compete; they complement each other.

**Q:** What is Amazon A2I (Augmented AI)?
**A:** A service to insert **human review** into ML workflows, e.g., when prediction confidence falls below a threshold.

**Q:** What are SageMaker Model Cards?
**A:** Structured model documentation: intended use, data, metrics, limitations, and risks. A governance tool.

**Q:** What are AWS AI Service Cards?
**A:** Transparency documentation that AWS publishes about its own AI services: intended use cases, limitations, and best practices.

**Q:** Explainability vs Interpretability?
**A:** Interpretable: the model is understandable by design (regression, trees). Explainable: the output of a complex model is justified post-hoc (SHAP, importances).

**Q:** What trade-off is usually present when requiring interpretability?
**A:** The most interpretable models are usually simpler and sometimes less accurate; with regulation in place, interpretability may weigh more than the last point of accuracy.

**Q:** What is a representative dataset and why does it matter?
**A:** One that reflects the diversity of the real population of use. It is the main lever to prevent bias before training.

**Q:** Measures against the risk of veracity in Gen AI for customers:
**A:** Grounding/RAG with citations, low temperature, guardrails, and human review in high-impact decisions.

**Q:** What is AI transparency?
**A:** Communicating what the system does, what data it uses, its limitations, and when the user is interacting with an AI.

---

## Domain 5 — Security, Compliance, and Governance

**Q:** What is the principle of least privilege?
**A:** Granting only the essential IAM permissions for the task (e.g., invoking a specific Bedrock model and nothing else).

**Q:** IAM roles vs. access keys in applications?
**A:** AWS applications must assume **roles** (temporary credentials), not carry embedded static access keys.

**Q:** What does AWS KMS do?
**A:** Encryption key management. With customer managed keys, you control policy, rotation, and auditing of encryption at rest (S3, EBS, Bedrock...).

**Q:** What does AWS CloudTrail record?
**A:** API calls in the account: who, what, when, and from where. It is the audit trail (e.g., Bedrock invocations).

**Q:** CloudTrail vs. CloudWatch?
**A:** CloudTrail: API call auditing (who did what). CloudWatch: operational metrics, logs, and alarms (how the system is performing).

**Q:** What does Amazon Macie do?
**A:** Discovers and classifies sensitive data (PII) in S3 using ML. Essential before using a data lake for training.

**Q:** Macie vs. GuardDuty vs. Inspector?
**A:** Macie: PII in S3. GuardDuty: threat detection/malicious activity in the account. Inspector: vulnerabilities in workloads (EC2, ECR, Lambda).

**Q:** What are VPC endpoints (PrivateLink) for?
**A:** Connecting the VPC to AWS services (e.g., Bedrock) without traversing the public internet: traffic stays within the AWS network.

**Q:** Shared responsibility model applied to Bedrock:
**A:** AWS secures the infrastructure and the service ("of the cloud"); the customer secures IAM, their data, configuration, and use of outputs ("in the cloud").

**Q:** What is AWS Artifact?
**A:** Self-service portal to download AWS compliance reports (SOC, ISO, PCI) and accept agreements.

**Q:** What does AWS Audit Manager do?
**A:** Continuously collects compliance evidence and maps it to frameworks (GDPR, ISO, PCI) to prepare for audits.

**Q:** AWS Config vs. Audit Manager?
**A:** Config continuously evaluates resource configuration against rules; Audit Manager collects evidence mapped to frameworks for audits.

**Q:** What is data residency and how is it respected with Bedrock?
**A:** Requirement that data does not leave a specific region/jurisdiction. Use the service in the chosen region; inference and customization are processed there, and data does not improve base models.

**Q:** What is data lineage and why does it matter in AI governance?
**A:** The trace of data origins and transformations leading to the model. It enables auditing of quality, permissions, and lifecycle compliance.

**Q:** AgentCore Identity vs Policy in AgentCore?
**A:** Identity authenticates workloads/users and manages credentials; Policy authorizes which Gateway tool each principal can invoke and under what conditions via Cedar.