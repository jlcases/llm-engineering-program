# Domain 3 Guide — Applications of Foundation Models (~28% of the exam)

> The domain with the **highest weight** on the exam. Covers how FMs are applied in practice: model selection criteria, in-depth prompt engineering, RAG and vector stores, fine-tuning, agents, and how to evaluate the resulting application. Many questions are "which approach/service do I choose?" scenarios.

## 1. Criteria for choosing a foundation model

Factors the exam expects you to weigh:

- **Cost** (per token, per instance hour, provisioned vs on-demand).
- **Latency**: smaller models respond faster; this matters for real-time chatbots.
- **Modality**: text, image, embeddings, multimodal.
- **Context window**: long documents → large window.
- **Supported languages**, domain quality, model size (capacity vs cost/latency).
- **Available customization**: does it allow fine-tuning? continued pre-training?
- **License and provider** (open-source vs proprietary models).
- Classic tradeoff: **large model = more capacity, higher cost and latency**; small model = cheaper/faster, less capable. There is no "best model": it depends on the use case.

## 2. Prompt engineering (in-depth)

- **Parts of a prompt**: instruction, context, input data, output indicator (desired format).
- **Zero-shot**: only the instruction, no examples.
- **Few-shot**: include input→output examples in the prompt to guide format and style (one-shot = 1 example).
- **Chain-of-thought (CoT)**: ask for step-by-step reasoning ("think step by step"); improves logic/math tasks.
- **Prompt templates**: reusable templates with variables.
- **Negative prompting**: explicitly indicate what NOT to do/include.
- **System prompt / role**: sets the global behavior of the assistant.
- Best practices: clear and specific instructions, delimiters to separate context, specify output format, iterate and evaluate.

### Versioning and Amazon Bedrock Prompt Management

- Treat the prompt as a versioned artifact: stable identifier, immutable version, declared variables, model configuration, author, date, and change notes.
- **Amazon Bedrock Prompt Management** allows you to create, save, test, and version prompts and their variants for reuse in applications and workflows.
- Compare versions with the same dataset and metrics before promoting them; keep an older version for rollback.
- Separate the prompt version from the model version and the evaluation dataset version. Changing any of these can alter the result.

### Prompting risks (prompt attacks)
- **Prompt injection**: malicious instructions injected into the input (or into retrieved documents — indirect injection) to hijack behavior.
- **Jailbreaking**: techniques to bypass the model's security policies.
- **Prompt leaking**: getting the model to reveal its system prompt or internal data.
- Mitigations: Bedrock **Guardrails**, input validation/sanitization, separate instructions from data, least privilege for model tools.

## 3. RAG and vector databases

- **RAG**: (1) user query → (2) search for relevant chunks by embedding similarity in a vector store → (3) inject them into the prompt → (4) the LLM responds **grounded** in that data.
- Benefits: up-to-date and proprietary knowledge, fewer hallucinations, source citation, no retraining cost.
- **Chunking**: splitting documents into chunks for indexing; chunk size affects retrieval quality.
- **Amazon Bedrock Knowledge Bases**: fully managed RAG — connects S3/Confluence/Salesforce/SharePoint/web, manages chunking, embeddings (e.g., Titan Embeddings) and the vector store, and responds with citations.
- **Vector stores cited in objective 3.1**: Amazon **OpenSearch Service**, **Aurora**, **Neptune**, and **RDS for PostgreSQL**. OpenSearch and PostgreSQL with pgvector are the most frequent distractors in RAG scenarios.

## 4. Customization: when to use each technique

Ladder from lowest to highest cost/complexity:

1. **Prompt engineering** — no data, no training. Always first.
2. **RAG** — updatable external knowledge; does not change the model.
3. **Fine-tuning** — changes weights with **labeled** data; for style, format, specific task. **PEFT/LoRA** reduces cost by training few parameters.
4. **Continued pre-training** — **unlabeled** domain data for vocabulary/jargon.
5. **Training from scratch** — practically never.

Data preparation for fine-tuning: quality over quantity, representative and clean data, prompt-completion pair format, curation and governance (data curation). In Bedrock, fine-tuning creates a **custom model** that requires **provisioned throughput** for serving.

## 5. Agents (agents for generative AI)

- An **agent** uses an LLM to **plan and execute multi-step tasks**, deciding which **tools/APIs** to call (ReAct-style reasoning: think → act → observe).
- **Amazon Bedrock Agents**: managed agents — **action groups** (APIs/Lambda that the agent can invoke, defined with OpenAPI schemas), integration with **Knowledge Bases**, session memory, and reasoning traces.
- Exam scenario: "the chatbot must query order status via an API and also respond with the return policy" → Bedrock Agent with action group + Knowledge Base.

## 6. Evaluating Applications with FMs

- Automatic metrics: **ROUGE** (summarization), **BLEU** (translation), **BERTScore** (semantic similarity), exact match/F1 (QA).
- **Human evaluation**: subjective quality, tone, utility.
- **LLM-as-a-judge**: a model evaluates another model's outputs (scalable, cheaper than humans).
- **Bedrock model evaluation**: automatic evaluation jobs (accuracy, robustness, toxicity) or with human workforce.
- Also evaluate the **business**: user satisfaction, resolution rate, cost per query, latency.
- For RAG: retrieval quality (did it retrieve relevant content?) and generation quality (faithfulness to context).
- For agents and workflows: completion rate, correct tool selection, success per step, error recovery, human interventions, end-to-end cost and latency.
- Evaluate the **entire system**, not just the FM: a good final response can mask unsafe steps or unnecessary calls.

## 7. Supporting Architectures and Services

- **Amazon S3**: source document storage for Knowledge Bases and training data.
- **AWS Lambda**: action group logic and serverless glue code.
- **API Gateway**: expose the generative app as an API.
- **Step Functions**: workflow orchestration.
- **CloudWatch**: application metrics and logs (invocations, latency).
- **Bedrock Playgrounds**: manual experimentation before converting the prompt and configuration into evaluable code.

## 8. Common Exam Traps

- **"Constantly changing data" → RAG**, not fine-tuning. **"Adopt a consistent brand tone/style" → fine-tuning**, not RAG.
- **Few-shot vs fine-tuning**: if a few examples in the prompt suffice, few-shot is cheaper and usually the "least effort" answer.
- **CoT**: the answer to "the model fails on multi-step reasoning problems" is chain-of-thought, not increasing temperature.
- **Knowledge Bases vs Agents**: only respond with documents → Knowledge Base; **execute actions**/call APIs → Agents (with action groups).
- **Chunking**: appears as part of the RAG pipeline (questions about "what step is missing between ingestion and embedding?").
- **Embeddings model vs text model**: to index documents, use an **embedding model** (Titan Embeddings), not the generative LLM.
- **ROUGE vs BLEU**: summarization → ROUGE; translation → BLEU. They ask this directly.
- **Model size tradeoff**: "reduce latency and cost accepting slightly lower quality" → smaller model; never "more provisioned throughput" if the problem is model size.
- **Temperature for factual tasks**: support/factual apps → low temperature; creativity (marketing) → high.
- **Prompt injection**: mitigation in AWS is **Bedrock Guardrails** + input validation; "retraining the model" is a distractor.
- **Custom model in Bedrock** → requires **provisioned throughput** (not served on-demand).
- **New prompt in production**: version it in Bedrock Prompt Management, evaluate with a stable dataset, and maintain rollback; copying text manually between environments is not a strategy.

## 9. Review Mini-Scenarios (Exam Format)

- *"The assistant must answer about the catalog, which changes weekly."* → RAG with Bedrock Knowledge Bases.
- *"The model must classify tickets following exactly our 5-category format; we have 20 examples."* → Few-shot prompting (before fine-tuning).
- *"The model fails on multi-step calculations."* → Chain-of-thought prompting.
- *"The chatbot must query order status via our API and cancel it if the customer requests."* → Bedrock Agent with action groups.
- *"Additionally, it must answer questions about the return policy (PDFs in S3)."* → Associate a Knowledge Base with the agent.
- *"What step converts documents into indexable chunks?"* → Chunking, then embeddings to the vector store.
- *"Malicious users cause the bot to ignore its instructions."* → Prompt injection → Bedrock Guardrails + input validation.
- *"Choose a model for a high-concurrency chatbot sensitive to latency and cost."* → Smaller/faster model, even if it sacrifices some quality.
- *"Measure if the summarizer covers the reference content."* → ROUGE.
- *"Evaluate thousands of responses without human annotator costs."* → LLM-as-a-judge (or automatic Bedrock model evaluation).
- *"Compare a new template with the production version and be able to roll back."* → Bedrock Prompt Management + versioned evaluation.
- *"The agent responds well but executes unnecessary tools and fails intermediate steps."* → Evaluate the application/agent step-by-step and end-to-end, not just the final text.
- *"Serve the fine-tuned model in Bedrock in production."* → Provisioned throughput.
- *"Where do I store embeddings in AWS?"* → OpenSearch Service/Serverless (or pgvector in Aurora/RDS).

## 10. Quick Glossary

| Term | Exam Definition |
|---|---|
| Zero-shot | Prompt without examples |
| Few-shot | Prompt with input→output examples |
| Chain-of-thought | Requesting step-by-step reasoning |
| Prompt template | Reusable prompt template with variables |
| Prompt Management | Bedrock service to save, test, version, and reuse prompts |
| Negative prompt | Indicate what it should NOT do/include |
| Prompt injection | Malicious input that hijacks instructions |
| Jailbreaking | Bypassing the model's security policies |
| Prompt leaking | Extracting the system prompt or internal data |
| Chunking | Splitting documents into indexable chunks |
| Vector store | Embedding database with similarity search |
| Grounding | Anchoring the response to retrieved sources |
| Action group | Set of APIs/Lambda that a Bedrock Agent can invoke |
| ReAct | Reason-Act-Obsserve pattern for agents |
| PEFT / LoRA | Efficient fine-tuning by training few parameters |
| Instruction tuning | Fine-tuning with instruction→response pairs |
| LLM-as-a-judge | An LLM evaluates another's outputs |
| Latency vs throughput | Time per response vs volume processed per unit time |

## 11. Pre-Exam Checklist

- [ ] I list FM selection criteria: cost, latency, modality, context window, customization, license.
- [ ] I distinguish zero-shot, few-shot, and chain-of-thought and when to apply each.
- [ ] I version prompts with Bedrock Prompt Management, evaluation dataset, and rollback.
- [ ] I explain the complete RAG pipeline: ingestion → chunking → embeddings → vector store → retrieval → generation.
- [ ] I know what Bedrock Knowledge Bases manage and what sources they accept.
- [ ] I distinguish Knowledge Base (respond with documents) from Agent (execute actions).
- [ ] I know what an action group is and that it is defined with API schemas.
- [ ] I place ROUGE, BLEU, BERTScore, and LLM-as-a-judge in the correct task.
- [ ] I evaluate RAG, agents, and workflows by component and also end-to-end.
- [ ] I identify prompt injection/jailbreak/leaking and their mitigations.
- [ ] I remember that custom models in Bedrock require provisioned throughput.
- [ ] Faced with "least effort/cost", I mentally try prompt engineering → RAG → fine-tuning in that order.

## 12. How to Read Questions in This Domain

Domain 3 scenario questions almost always hide the answer in a constraint:

1. Mentally highlight the operational constraint: "least effort", "lowest cost", "data changes daily", "must call an API", "no internet access", "consistent brand voice".
2. Map the constraint to the technique: effort/cost → prompt engineering; changing data → RAG; actions → Agents; consistent style → fine-tuning.
3. Eliminate distractors that solve **another** problem (retraining when the problem is fresh knowledge; increasing throughput when the problem is model size).
4. Between two valid options, the **managed** and **cheapest** one that meets all requirements wins.

## Mapping to the repo

This domain is the practical core of the program: **module 2 (prompt engineering), module 3 (RAG and evaluation), and module 4 (agents, Bedrock Agents, MCP)**.

---

> ⚠️ **Note**: the content, weights, and services cited may change. Coverage cross-checked with
> the [official objectives for Domain 3](https://docs.aws.amazon.com/aws-certification/latest/ai-practitioner-01/ai-practitioner-01-domain3.html)
> on **August 21, 2026**.
