# Domain 2 Guide — Fundamentals of Generative AI (~24% of the exam)

> This domain covers core generative AI concepts (tokens, embeddings, foundation models, the FM lifecycle), their use cases and limitations, and the current AWS layer: **Amazon Bedrock**, SageMaker AI/JumpStart, Amazon Quick, Kiro, Strands Agents, and Amazon Bedrock AgentCore.

## 1. Core Generative AI Concepts

- **Generative AI**: the ability to **generate new content** (text, image, audio, code, or video) from learned patterns. Modern systems typically use deep learning, but GenAI describes the capability, not a strict step in the AI → ML → DL hierarchy.
- **Foundation Model (FM)**: a large model pre-trained on massive datasets and adaptable to many tasks without training from scratch. **LLMs** are language-focused FMs.
- **Token**: the smallest unit an LLM processes (subwords, ~4 characters in English). Cost and context limits are measured in tokens.
- **Tokenization**: converting text into tokens (BPE, WordPiece).
- **Embedding**: a **numerical vector representation** of text (or image) that captures its semantic meaning; similar texts → close vectors. The basis of semantic search and RAG.
- **Vector database**: stores embeddings and enables similarity search. Guide 1.1 cites Amazon OpenSearch Service, Aurora, Neptune, and RDS for PostgreSQL.
- **Context window**: the maximum number of tokens (input + output) the model handles in a single call.
- **Transformer**: an architecture based on **self-attention** that processes sequences in parallel and captures long-range relationships; it is the foundation of modern LLMs.
- Other generative models you may encounter: **diffusion models** (images: noise → image, e.g., Stable Diffusion), GANs, VAEs, and **multimodal** models (text+image).

### Context engineering

**Context engineering** is designing everything the model receives in an invocation so it has the correct information at the right time. It goes beyond writing the prompt: it selects and orders instructions, history, memory, documents retrieved by RAG, tool results, examples, and metadata, respecting the context window and token budget.

- Prioritize relevant, recent, and reliable information; more context does not always yield higher quality.
- Separate instructions, untrusted data, and tool results to reduce prompt injection.
- Summarize or selectively retrieve memory instead of forwarding entire conversations.
- Measure quality, latency, and cost: every input token also consumes window space and may be billed.

### Agentic AI Fundamentals

- An **agent** combines a model with a goal, instructions, memory, and **tools** to observe, decide, and act.
- **Orchestration** controls the sequence, states, retries, approvals, and execution limits.
- **Memory** can be short-term (session state) or persistent (selected preferences and facts); it is not equivalent to forwarding the entire history.
- **MCP (Model Context Protocol)** standardizes how an AI application discovers and uses tools, resources, and context from external systems.
- In a **multi-agent** pattern, specialized agents collaborate, delegate, or review tasks. It provides separation of responsibilities but also adds cost, latency, and failure points; it is not better by default.

## 2. How an LLM Generates Text

- Predicts the **next token** probabilistically and repeats (autoregressive).
- The output is **non-deterministic**: the same input can yield different outputs.
- **Inference parameters**:
  - **Temperature**: scales the randomness of the distribution. Low (→0) = more deterministic and repeatable outputs; high = more creative/diverse.
  - **Top-p (nucleus sampling)**: limits the choice to tokens whose cumulative probability is ≤ p.
  - **Top-k**: limits the choice to the k most probable tokens.
  - **Max tokens / response length**: the cap on generated tokens (controls cost and latency, not quality).
  - **Stop sequences**: strings that halt generation.

## 3. Foundation Model Lifecycle

1. **Data selection**: massive corpus (often self-supervised, without manual labels).
2. **Pre-training**: learning general language by predicting tokens; extremely expensive (GPUs, weeks).
3. **Continued pre-training**: continuing pre-training with **unlabeled domain data** (medical jargon, legal...).
4. **Fine-tuning**: adjusting weights with **labeled** task data (instruction tuning with prompt-response pairs).
5. **RLHF (Reinforcement Learning from Human Feedback)**: aligning the model with human preferences using a reward model.
6. **Evaluation**: benchmarks and metrics (see §6).
7. **Deployment and iteration.**

## 4. Use Cases, Advantages, and Limitations

- **Use cases**: chatbots and assistants, summarization, code generation and explanation, extraction and classification, translation, semantic search, image generation, agents.
- **Advantages**: adaptability to many tasks, little to no proprietary training data (zero/few-shot), fast time-to-market.
- **Exam-focused limitations**:
  - **Hallucinations**: fluent but false answers, stated with confidence. Mitigation: RAG/grounding, human review, low temperature, Guardrails with contextual grounding check.
  - **Knowledge cutoff**: the model does not know facts post-training → use RAG for current data.
  - **Non-determinism**, biases inherited from data, risk of data exposure (prompt injection, PII leakage), inference cost, **lack of interpretability** (FMs are less explainable than a decision tree).

## 5. How to Adapt an FM (from cheapest to most expensive)

1. **Prompt engineering**: instructions and examples in the prompt; without touching weights.
2. **RAG (Retrieval-Augmented Generation)**: retrieve relevant documents from an external source (vector DB) and inject them into the prompt. Provides access to **proprietary and up-to-date data without retraining**; reduces hallucinations; knowledge is updated by updating the database, not the model.
3. **Fine-tuning**: partially retrain weights with labeled data; changes **behavior/style/task**. Efficient variants: **PEFT/LoRA** (train few additional parameters).
4. **Train from scratch**: almost never the correct answer (extreme cost).

Exam rule: "up-to-date or proprietary knowledge" → **RAG**; "consistent tone, format, or specialized task" → **fine-tuning**; "minimum cost/effort" → **prompt engineering**.

## 6. Evaluating Generative Models

- **ROUGE**: overlap with reference; typical for **summarization**.
- **BLEU**: n-gram precision; typical for **translation**.
- **BERTScore**: semantic similarity with embeddings (not just exact words).
- **Perplexity**: how "surprised" the model is by the text; lower = better language modeling.
- **Human evaluation / LLM-as-a-judge**: useful for overall quality.
- Benchmarks: MMLU, HELM, etc. (just know they exist and what they are for).
- In AWS: **Amazon Bedrock model evaluation** (automated or with human review) and **SageMaker Clarify** for FM evaluation.

## 7. Generative AI on AWS

- **Amazon Bedrock**: a **serverless and fully managed** service for invoking FMs from multiple providers (Amazon Titan/Nova, Anthropic Claude, Meta Llama, Mistral, Cohere, Stability AI...) via a **single API**. No infrastructure to manage. Key components:
  - **Model choice**: compare and switch models without changing platforms; playgrounds for experimentation.
  - **Knowledge Bases**: **managed RAG** — ingestion from S3 and other sources, chunking, embeddings, and managed vector store.
  - **Agents**: orchestrate multi-step tasks by calling APIs/Lambda (action groups) and Knowledge Bases.
  - **Guardrails**: content filters, denied topics, PII redaction, contextual grounding (Domain 4).
  - **Custom models**: fine-tuning and continued pre-training on certain models; customer data is **not** used to train base models.
  - **Provisioned throughput** vs **on-demand** (see §8 pricing).
- **Amazon SageMaker JumpStart**: hub of FMs and pre-trained models for **deploying on your own SageMaker infrastructure** with more control (instances, networks) and fine-tuning; more flexibility, more management.
- **Amazon Q Developer**: code assistant (autocomplete, chat, security) — successor to CodeWhisperer.
- **Amazon Q Business**: enterprise generative assistant connected to corporate data with permissions.
- **Amazon Quick**: managed workspace with chat, agents, analysis/visualization, research, and automation on connected data. Amazon Quick Sight is its BI capability.
- **Kiro**: agentic IDE oriented toward specification-driven development, steering files, and quality hooks.
- **Strands Agents**: open-source SDK and model-first approach for building agents with tools, multiple providers, and protocols like MCP.
- **Amazon Bedrock AgentCore**: model- and framework-agnostic infrastructure for deploying and operating agents. Includes Runtime, Gateway, Memory, Identity, Observability, Evaluations, and Policy.
- **AWS Transform**: agentic service for modernizing applications and workloads; it is on the list of services in scope for the 1.1 review.
- **Amazon Titan / Nova**: Amazon's own FM families (text, embeddings, image).
- Infrastructure: **AWS Trainium** (chip for training), **AWS Inferentia** (chip for inference), NVIDIA GPUs on EC2.

## 8. Bedrock Pricing and Throughput

- **Token-based pricing**: inference is typically charged per input and output tokens. A longer context can increase cost and latency even before generating the response.
- **On-demand**: pay-per-token (input + output); no commitment; for variable workloads or experimentation.
- **Provisioned throughput**: reserved capacity (model units) with a time commitment; for sustained, predictable production workloads; **mandatory for custom/fine-tuned models**.
- **Batch inference**: process batches with a discount when there is no urgency.
- Cost levers: smaller model, fewer tokens (concise prompts, output limits), caching, batch.

## 9. Common Exam Traps

- **Bedrock vs SageMaker JumpStart**: serverless API without managing infrastructure → **Bedrock**; infrastructure/instance control and deep customization → **JumpStart**.
- **RAG vs fine-tuning**: "internal documents that change daily" → RAG (Knowledge Bases), not fine-tuning.
- **Continued pre-training vs fine-tuning**: **unlabeled** domain data → continued pre-training; labeled prompt-response pairs → fine-tuning.
- **Temperature vs top-p vs max tokens**: "more consistent/repeatable responses" → lower temperature; "limit length and cost" → max tokens.
- **Embeddings**: if the question mentions "semantic search" or "meaning similarity" → embedding model + vector DB, not a chat LLM.
- **Hallucinations**: the correct mitigation is usually **RAG/grounding + human oversight**, not "more temperature" or "more tokens".
- **Amazon Q Developer vs Q Business**: code for developers vs assistant on company data.
- **Prompt engineering vs context engineering**: the former designs instructions and examples; the latter also designs memory, retrieval, tools, history, and context budget.
- **Single agent vs multi-agent**: use multiple agents only when specialization or review compensates for the added coordination, cost, and latency.
- **Strands vs AgentCore**: Strands is an SDK for building logic; AgentCore provides managed infrastructure to execute, connect, remember, authorize, and observe agents built with Strands, LangGraph, CrewAI, or custom code.
- **Bedrock Agents vs AgentCore**: Bedrock Agents offers managed orchestration with action groups and knowledge bases; AgentCore hosts and operates agent code from any framework.
- **Knowledge cutoff**: "the chatbot doesn't know about products launched last month" → RAG, not retraining from scratch.
- **Provisioned throughput**: appears as the correct answer when the scenario requires **guaranteed performance** for production or **using a fine-tuned model** on Bedrock.

## 10. Review Mini-Scenarios (Exam Format)

- *"We want to test various FMs from different providers with a single API and without managing servers."* → Amazon Bedrock.
- *"We need to deploy an open-source model with full control over instances and networking."* → SageMaker JumpStart.
- *"The chatbot invents answers about internal policies."* → RAG with Bedrock Knowledge Bases (grounding), not fine-tuning.
- *"We want the model to always write in the firm's legal tone."* → Fine-tuning (labeled example data).
- *"We have 50 GB of unlabeled medical reports and the model doesn't understand the jargon."* → Continued pre-training.
- *"Support assistant responses must be consistent and repeatable."* → Lower temperature (≈0).
- *"We need to shorten responses to reduce cost."* → Limit max tokens.
- *"The agent receives history, memory, documents, and tools, but exceeds the window and loses instructions."* → Apply context engineering: select, order, and budget the context.
- *"Multiple agents must discover external tools with a common interface."* → MCP for connection; orchestration for coordinating the workflow.
- *"What metric to evaluate the news summarizer?"* → ROUGE.
- *"What metric to evaluate the translator?"* → BLEU.
- *"Search for products semantically similar to the user's query."* → Embeddings (Titan Embeddings) + vector database.
- *"Developers want AI-powered code autocompletion."* → Amazon Q Developer.
- *"Employees asking about internal documentation with corporate permissions."* → Amazon Q Business.
- *"Analyze data, research, and automate business work via chat and agents without building a custom platform."* → Amazon Quick.
- *"Build a model-first, open-source agent in Python connected to tools."* → Strands Agents.
- *"Host a LangGraph agent with isolated runtime, managed memory, identity, gateway, and observability."* → Amazon Bedrock AgentCore.
- *"Agent development guided by specifications, steering, and quality hooks."* → Kiro.
- *"Production with high and sustained traffic, and a fine-tuned model on Bedrock."* → Provisioned throughput.

## 11. Quick Glossary

| Term | Exam Definition |
|---|---|
| Foundation model | Large pre-trained model adaptable to many tasks |
| LLM | FM specialized in natural language |
| Token | Text unit processed by the model (~subword) |
| Embedding | Numerical vector representing meaning |
| Context window | Maximum tokens per invocation (input+output) |
| Temperature | Control of generation randomness |
| Top-p / top-k | Restriction on candidate token sampling |
| Prompt | Input with instructions/context for the model |
| Inference | Generation of the model's response |
| Pre-training | Initial massive self-supervised training |
| Fine-tuning | Weight adjustment with labeled task data |
| RLHF | Alignment with human preferences via reward model |
| RAG | Retrieve external context and inject it into the prompt |
| Hallucination | Plausible but factually false output |
| Multimodal | Model combining modalities (text+image...) |
| Diffusion model | Image generator via noise elimination |
| Agent | LLM that plans and executes actions with tools |
| Context engineering | Selection and composition of instructions, memory, retrieval, tools, and history within the context budget |
| MCP | Protocol for connecting AI applications with external tools, resources, and context |

## 12. Pre-exam Checklist

- [ ] I know what a token, an embedding, and a context window are, and that tokens are billed.
- [ ] I can distinguish prompt engineering from context engineering and know how to budget memory, RAG, tools, and history.
- [ ] I can explain agent, tool, memory, orchestration, MCP, and when a multi-agent pattern is worthwhile.
- [ ] I can explain temperature, top-p, top-k, max tokens, and stop sequences and what each adjusts.
- [ ] I can order the prompt engineering ladder → RAG → fine-tuning → continued pre-training → from scratch by cost.
- [ ] I can distinguish fine-tuning (labeled) from continued pre-training (unlabeled).
- [ ] I associate ROUGE↔summary, BLEU↔translation, BERTScore↔semantic similarity, perplexity↔modeling.
- [ ] I can distinguish Bedrock (serverless, API) from SageMaker JumpStart (your infra, more control).
- [ ] I can list Bedrock components: Knowledge Bases, Agents, Guardrails, model evaluation, custom models.
- [ ] I know when to choose on-demand, provisioned throughput, and batch inference.
- [ ] I can distinguish Amazon Q Developer, Q Business, and Amazon Quick.
- [ ] I can distinguish the Strands Agents SDK, Bedrock Agents, and the Amazon Bedrock AgentCore infrastructure.
- [ ] I know what Kiro and AWS Transform are used for in the current scope.
- [ ] I know that Trainium trains and Inferentia serves inference.

## Mapping to the repo

This domain corresponds to **modules 1 (foundations and Bedrock) and 2 (basic prompting)**, with support from module 3 for embeddings/RAG.

---

> ⚠️ **Note**: the content, weights, and services cited may change. Coverage verified against
> the [official objectives for Domain 2](https://docs.aws.amazon.com/aws-certification/latest/ai-practitioner-01/ai-practitioner-01-domain2.html)
> on **August 21, 2026**.
