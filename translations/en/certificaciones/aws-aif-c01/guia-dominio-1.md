# Domain 1 Guide — Fundamentals of AI and ML (20% of the exam)

> This domain asks about basic AI/ML concepts, types of learning, use cases,
> inference, and lifecycle. Revision 1.1 explicitly adds **agentic AI**, the choice
> between traditional ML and foundation models, and current services such as Amazon Bedrock, Amazon Q,
> Amazon Quick, and Kiro.

## 1. Basic Concepts: AI, ML, Deep Learning, GenAI, and Agentic AI

- **Artificial Intelligence (AI)**: broad field; any technique that enables a machine to mimic human intelligent behavior (includes rule-based systems, not just learning).
- **Machine Learning (ML)**: subset of AI; the system learns patterns from data rather than explicitly programmed rules.
- **Deep Learning (DL)**: subset of ML based on neural networks with multiple layers; excels in unstructured data (images, audio, text).
- **Generative AI (GenAI)**: creates new content—text, images, audio, video, or code—based on learned patterns. Modern LLMs and other foundation models typically use deep learning.
- **Agentic AI**: systems that pursue a goal through planning, memory, tools, and one or more agents. It is not an additional level in the hierarchy: it is an application pattern that typically uses generative models.
- Exam-safe relationship: **ML is part of AI and DL is part of ML**. GenAI describes what the system produces; agentic AI describes how it organizes actions to achieve a goal. Avoid treating them as strictly interchangeable subsets.
- **Structured data** (tables, CSV) vs **unstructured** (text, images, audio) vs **semi-structured** (JSON, XML). DL shines in unstructured data; classical ML is often sufficient for tabular data.

## 2. Types of Learning

| Type | Data | Use Cases |
|---|---|---|
| **Supervised learning** | Labeled (features + label) | Spam classification, price prediction (regression) |
| **Unsupervised learning** | Unlabeled | Customer clustering, anomaly detection, dimensionality reduction |
| **Semi-supervised** | Few labeled + many unlabeled | Classification with expensive labeling |
| **Reinforcement learning (RL)** | Agent + environment + rewards | Robotics, control, and games |
| **Self-supervised** | Labels come from the data itself | LLM pre-training (predicting the next token) |

- **Classification** (discrete label: binary or multi-class) vs **regression** (continuous value). If the question says "predict price / demand / a number" → regression; "classify into categories / detect yes-no fraud" → classification.
- **Clustering** has no labels: if the scenario says "group similar customers without predefined categories" → unsupervised (K-means).

## 3. ML Lifecycle (ML lifecycle)

1. **Business problem definition** (Do you even need ML? If fixed rules suffice, do not use ML).
2. **Data collection and preparation**: cleaning, handling missing values, **feature engineering**, train/validation/test split.
3. **Training**: algorithm selection, tuning **hyperparameters** (set by the human before training) vs **parameters/weights** (learned by the model).
4. **Evaluation**: metrics on test data the model has not seen.
5. **Deployment**: real-time endpoint vs batch inference.
6. **Monitoring**: detection of **data drift** and **model drift**; retraining.
- **MLOps**: applying DevOps practices to the ML lifecycle (automation, CI/CD of models, data and model versioning, continuous monitoring).

### Sources and Ways to Serve Models

- **Open source pre-trained model**: accelerates startup and allows inspection or self-hosting, but the team assumes evaluation, security, capacity, and operations.
- **Custom model**: maximum control and specialization; requires data, compute, expertise, and maintenance.
- **Managed API**: lower operational burden and scaling delegated to the provider.
- **Self-hosted API**: more control over infrastructure, residency, and optimization, in exchange for operating the service.

## 4. Overfitting, Underfitting, and Model Quality

- **Overfitting**: excellent on training, poor on test → memorizes instead of generalizing. Mitigation: more data, regularization, early stopping, dropout, simpler models.
- **Underfitting**: poor on training and on test → model too simple or insufficient data/features.
- **Bias-variance tradeoff**: high bias ≈ underfitting; high variance ≈ overfitting.

## 5. Technical and Business Metrics

- **Classification**: confusion matrix, **accuracy** (misleading with imbalanced classes), **precision** (of what I predicted positive, how many I got right — matters when false positive is costly), **recall** (of the actual positives, how many I detected — matters when false negative is costly, e.g., cancer detection or fraud), **F1** (harmonic mean of both), **AUC-ROC**.
- **Regression**: MAE, MSE, **RMSE**, R².
- **Business**: cost per user or interaction, development cost, customer satisfaction and feedback, completion rate, and **ROI**. A technically superior model adds no value if it worsens cost, latency, or business outcome.
- Exam tip: "detect as many fraud cases as possible even if there are false alarms" → maximize **recall**; "avoid accusing innocent customers" → **precision**.

## 6. Inference: Modalities

- **Real-time inference**: low latency, always-on endpoint, sustained traffic.
- **Batch (transform)**: large volumes with no urgency; lower cost, no persistent endpoint.
- **Asynchronous inference**: large payloads, latency-tolerant, request queue.
- **Serverless inference**: intermittent or unpredictable traffic, pay-per-use, tolerates cold starts.

## 7. Choosing Traditional ML, a Foundation Model, or Rules

| Approach | Best Fit |
|---|---|
| Deterministic rules | Exact outcome, stable policy, and explainable logic; no prediction needed |
| Traditional ML | Tabular data or time series, bounded objective, lower cost/latency, and high explainability |
| Foundation model | Text, image, or open-ended tasks; generation, summarization, conversation, and cross-domain adaptation |
| Agentic system | Multi-step objective requiring tools, memory, decision-making, and orchestration |

In regulated sectors, explainability, privacy, cost, and operational constraints
may make a traditional model preferable even if an FM can solve the task.

## 8. AWS AI/ML Services: Which to Choose

General exam rule: **if a managed AI service exists that solves the use case, it is the answer** (lowest operational effort); SageMaker AI is for when you need to build or train your own models.

### Pre-trained AI Services (No ML Expertise Required)
- **Amazon Comprehend**: NLP on text — sentiment, entities, key phrases, PII detection, document classification.
- **Amazon Rekognition**: vision — objects, faces, content moderation in images and video, text in images.
- **Amazon Textract**: **extract text, tables, and forms from scanned documents/PDFs** (more than simple OCR: understands structure).
- **Amazon Transcribe**: speech-to-text (audio → text).
- **Amazon Polly**: text-to-speech (text → voice).
- **Amazon Translate**: automatic translation between languages.
- **Amazon Lex**: conversational chatbots with voice and text (the Alexa engine).
- **Amazon Kendra**: **intelligent enterprise search** with natural language over document repositories.
- **Amazon Personalize**: personalized recommendations (Amazon.com style) without ML expertise.
- **Amazon Q Business**: generative enterprise assistant over company data.

### Platform, Foundation Models, and Agentic Work

- **Amazon Bedrock**: managed API access to foundation models and capabilities to create GenAI applications and agents without managing model infrastructure.
- **Amazon SageMaker AI**: platform to create, train, adapt, deploy, and monitor models with greater control over the ML lifecycle.
- **SageMaker JumpStart**: catalog and starting point for pre-trained models and solutions within SageMaker AI.
- **Amazon Q**: family of assistants for enterprise work and software development.
- **Amazon Quick**: AI workspace to research, analyze data, visualize, and automate work with chat and agents.
- **Kiro**: agentic development environment guided by specifications, steering, and hooks.
- **Strands Agents**: open-source SDK to build agents; **Amazon Bedrock AgentCore** provides managed infrastructure to run and operate them.
- **Amazon Nova**: family of AWS foundation models available in the Bedrock ecosystem.
- **AWS Transform**: agentic service to modernize applications and workloads.

### Human in the Loop
- **Amazon A2I (Augmented AI)**: incorporates **human review** of low-confidence predictions (e.g., reviewing questionable Textract extractions).

## 9. Common Exam Traps

- **AI vs ML vs DL**: if the system uses fixed, hand-written rules, it is AI but **not** ML.
- **"No ML experience" / "least operational overhead"** → managed AI service (Comprehend, Rekognition...), **not** SageMaker AI.
- **Textract vs Rekognition**: documents/forms → Textract; photos/video/faces → Rekognition (although Rekognition also reads text in scene images, e.g., license plates).
- **Kendra vs Personalize**: document search → Kendra; product/content recommendations → Personalize.
- **Transcribe vs Polly**: they are inverses — audio→text vs text→audio. Read the conversion context carefully.
- **Hyperparameter vs parameter**: hyperparameter is set by the human before training (learning rate, epochs); parameter (weights) is learned by the model.
- **Accuracy with imbalanced classes**: a model that always says "no fraud" can have 99% accuracy and be useless → look at precision/recall/F1.
- **Inference type**: "millions of records every night" → batch; "immediate response to the user" → real-time; "sporadic and unpredictable traffic" → serverless.
- **Traditional ML vs FM**: bounded, explainable tabular prediction → Traditional ML; open-ended content generation or comprehension → FM.
- **Bedrock vs SageMaker AI**: consuming FMs via API with low operations → Bedrock; controlling training, infrastructure, or the ML lifecycle → SageMaker AI.
- **Strands vs AgentCore**: Strands builds the agent logic; AgentCore provides managed runtime and operational services.
- **When NOT to use ML?**: if the problem can be solved with simple deterministic logic or there is no data, the correct answer is not to use ML.

## 10. Mini-Review Scenarios (Exam Format)

- *"An insurer wants to predict next quarter's claim amounts with tabular data and needs to explain every decision."* → Regression with Traditional ML in SageMaker AI.
- *"Group support tickets into topics without predefined categories."* → Unsupervised learning (clustering).
- *"Extract amounts and fields from scanned PDF invoices."* → Amazon Textract.
- *"Analyze the sentiment of product reviews without an ML team."* → Amazon Comprehend.
- *"Convert company podcasts into text articles."* → Amazon Transcribe.
- *"Give a natural voice to a telephone assistant."* → Amazon Polly (+ Lex for conversation).
- *"Search thousands of internal documents with natural language questions."* → Amazon Kendra.
- *"Recommend movies based on each user's history."* → Amazon Personalize.
- *"Have a human review predictions with confidence < 80%."* → Amazon A2I.
- *"Summarize and answer open-ended questions about contracts via a managed API."* → Foundation model in Amazon Bedrock.
- *"Research a market, consult tools, and prepare a report in multiple steps."* → Agentic system; Amazon Quick for the managed workspace or Strands + AgentCore for a custom solution.
- *"Always apply the same discount according to a closed legal table."* → Deterministic rules, not ML.
- *"The model performs 99% on training and 60% on test."* → Overfitting; regularization/more data/early stopping.
- *"The team wants to train, tune, and deploy a custom model end-to-end."* → Amazon SageMaker AI.

## 11. Quick Glossary

| Term | Exam Definition |
|---|---|
| Feature | Model input variable |
| Label | Target value to be predicted (supervised) |
| Feature engineering | Creating/transforming features to improve the model |
| Training set | Data used for the model to learn |
| Validation set | Data to adjust hyperparameters |
| Test set | Unseen data to evaluate generalization |
| Epoch | One complete pass through the training set |
| Learning rate | Hyperparameter: size of the update step |
| Inference | Using the trained model to predict |
| Data drift | Production data changes relative to training data |
| Model drift | Model quality degrades over time |
| Confusion matrix | TP/FP/TN/FN table of a classifier |
| Ensemble | Combining multiple models to improve the result |
| Transfer learning | Reusing a pre-trained model on a new task |
| MLOps | DevOps applied to the ML lifecycle |

## 12. Pre-exam Checklist

- [ ] I explain the relationship between AI, ML, and DL, and why GenAI and agentic AI describe distinct capabilities or patterns.
- [ ] I distinguish supervised / unsupervised / semi-supervised / RL with an example of each.
- [ ] I distinguish classification vs regression vs clustering based on the problem statement.
- [ ] I know when to choose precision and when to choose recall (cost of FP vs FN).
- [ ] I explain overfitting vs underfitting and how to mitigate them.
- [ ] I know what each managed AI service does within scope (Comprehend, Rekognition, Textract, Transcribe, Polly, Translate, Lex, Kendra, and Personalize).
- [ ] I choose between traditional ML and foundation models based on task, explainability, cost, and operations.
- [ ] I distinguish between Bedrock, SageMaker AI, JumpStart, Amazon Q, Amazon Quick, Kiro, Strands Agents, and AgentCore.
- [ ] I correctly choose between real-time, batch, async, and serverless inference.
- [ ] I remember that "least operational overhead" points to the managed service.

## Mapping to the repo

This domain corresponds to **Module 1 (LLM Fundamentals and APIs)** and the evaluation section of **Module 2**.

---

## Verified Official Sources

- [AWS Certified AI Practitioner (AIF-C01) Official Guide](https://docs.aws.amazon.com/aws-certification/latest/ai-practitioner-01/ai-practitioner-01.html)
- [Domain 1 Objectives](https://docs.aws.amazon.com/aws-certification/latest/ai-practitioner-01/ai-practitioner-01-domain1.html)
- [Revision 1.1 Changes](https://docs.aws.amazon.com/aws-certification/latest/ai-practitioner-01/aif-01-revisions.html)
- [AWS Services Currently in Scope](https://docs.aws.amazon.com/aws-certification/latest/ai-practitioner-01/aif-01-in-scope-services.html)

> ⚠️ **Note**: Content, weights, and services may change. This guide was verified on
> **August 21, 2026**; check the official documentation before taking the exam.
