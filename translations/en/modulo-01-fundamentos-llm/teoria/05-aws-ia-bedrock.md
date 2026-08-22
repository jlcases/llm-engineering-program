# Generative AI Services on AWS: Bedrock, SageMaker JumpStart, and Amazon Q

> **Module 1 · Topic 5** · Estimated study time: 2.5 h
> Associated lab: `labs/05_bedrock_inference.py`
> Associated exercises: 8 and 10.

---

## 1. The Generative AI Landscape on AWS

AWS does not have "a" single AI service: it has a three-layer stack, and choosing the correct layer is your first architectural decision:

```
┌──────────────────────────────────────────────────────────────┐
│  APLICACIONES        Amazon Q  (asistentes listos para usar) │
├──────────────────────────────────────────────────────────────┤
│  PLATAFORMA LLM      Amazon Bedrock  (modelos via API,       │
│                      serverless: sin gestionar GPUs)         │
├──────────────────────────────────────────────────────────────┤
│  INFRAESTRUCTURA ML  SageMaker (+ JumpStart)                 │
│                      (entrenar, ajustar y servir TUS         │
│                      modelos en TUS instancias)              │
└──────────────────────────────────────────────────────────────┘
```

**Real estate analogy.** Amazon Q is a hotel (fully furnished, minimal customization). Bedrock is a furnished rental apartment (you bring your own clothes — prompts and data — and don't worry about the boiler). SageMaker is buying a plot of land and building (total control, and you're also responsible for maintenance).

### Amazon Q — The Application Layer

Packaged assistants: **Q Business** (chat over enterprise data, with connectors to S3, SharePoint, Confluence...) and **Q Developer** (code assistant, successor to CodeWhisperer, integrated into IDEs and the AWS console). You configure them; you don't code them. Good to know they exist; little to learn here for an LLM engineer.

### SageMaker JumpStart — The Infrastructure Layer

SageMaker is the general ML platform (notebooks, training, endpoints). **JumpStart** is its catalog of pre-trained models (Llama, Mistral, Falcon, embeddings...) deployable with a single click or a few lines of SDK **on GPU instances that you choose and pay for by the hour**. You use it when you need: open weights with full control, custom fine-tuning, or a model Bedrock doesn't offer. In exchange: you manage capacity, scaling, and fixed costs for every running instance.

### Bedrock — The Platform Layer (the one that matters)

Serverless API for **foundation models from multiple providers**. You pay per token, manage no infrastructure, and everything flows through IAM and AWS accounts. The rest of this topic covers Bedrock, as it's the typical path by which an enterprise already on AWS consumes LLMs.

---

## 2. Bedrock: Core Concepts

### 2.1 Multi-provider Foundation Models

Bedrock offers under a single API models from: **Anthropic** (Claude), **Meta** (Llama), **Mistral**, **Amazon** (its own **Nova** family, including Nova 2 Lite, and multimodal variants), Cohere, AI21, Stability, DeepSeek, and others. The value proposition:

- **A single bill and unified access control** (IAM) for all models.
- **Data never leaves your AWS perimeter** (chosen region, PrivateLink available, and AWS commits to not using your prompts for training).
- **Switching models = changing a string**, not rewriting the integration (thanks to the Converse API, §3.2).

Each model has a **model ID**. Verified examples as of August 2026: `amazon.nova-2-lite-v1:0` and `eu.anthropic.claude-haiku-4-5-20251001-v1:0`. The catalog changes and not all IDs are available in every region.

### 2.2 Access Enablement and Regions

Two specifics you will encounter on day one:

1. **Model access.** Before invoking a model, you must enable it in the console (*Bedrock → Model access*). Until then, the API returns `AccessDeniedException` even if your IAM is correct.
2. **Regions and inference profiles.** Not all models are available in all regions. Additionally, recent models often require invocation via **cross-region inference profiles**: IDs with a geography prefix (`us.`, `eu.`) that route the request across multiple regions to absorb spikes, e.g., `eu.anthropic.claude-haiku-4-5-20251001-v1:0`. If a "standard" model ID gives you an error telling you to use an inference profile, this is why.

### 2.3 Inference Modalities and Pricing

- **On-demand**: pay-per-token, no commitment. The default mode and the one used in the lab.
- **Batch**: asynchronous jobs on S3 files, with discounts, for non-interactive volume.
- **Provisioned throughput**: reserved capacity (per model unit) for sustained workloads with performance SLAs; also required to serve models with custom fine-tuning.

Specific pricing: always at https://aws.amazon.com/bedrock/pricing/ (varies by model, region, and modality; do not memorize them or hardcode them in code).

### 2.4 The Surrounding Ecosystem

To build your vocabulary (you will see these in later modules): **Knowledge Bases** (managed RAG over your data), **Agents** (tool orchestration), **Guardrails** (configurable content and PII filters), **Model evaluation**, and managed fine-tuning for select models.

---

## 3. The Bedrock API with boto3

Bedrock is split into **two boto3 clients**, and confusing them is error #1:

```python
import boto3

bedrock = boto3.client("bedrock", region_name="eu-west-1")          # plano de CONTROL
runtime = boto3.client("bedrock-runtime", region_name="eu-west-1")  # plano de DATOS
```

- `bedrock`: management — list models (`list_foundation_models`), fine-tuning, etc.
- `bedrock-runtime`: inference — where `invoke_model` and `converse` live.

### 3.1 The Legacy Path: `invoke_model`

Receives a JSON `body` **in each provider's native format**: Anthropic's (`anthropic_version`, `messages`...) looks nothing like Llama's or Titan/Nova's. Switching models meant rewriting the payload and parsing logic. You will see it in legacy code and need it for non-conversational models (embeddings, images).

### 3.2 The Modern Path: The Converse API

`converse` defines **a single message format for all text models**:

```python
response = runtime.converse(
    modelId="eu.anthropic.claude-haiku-4-5-20251001-v1:0",
    system=[{"text": "Eres un asistente conciso que responde en español."}],
    messages=[
        {"role": "user", "content": [{"text": "¿Qué es Amazon Bedrock?"}]}
    ],
    inferenceConfig={"maxTokens": 500, "temperature": 0.3, "topP": 0.9},
)

texto = response["output"]["message"]["content"][0]["text"]
uso   = response["usage"]          # inputTokens, outputTokens, totalTokens
parada = response["stopReason"]    # "end_turn", "max_tokens", ...
```

Notice the parallelism with what you already learned: `system` + a list of `messages` with roles (like OpenAI/Anthropic), `inferenceConfig` with the parameters from topic 3 (camelCase names), `usage` to count tokens, and `stopReason` to check for truncations. The structural difference: `content` is always a **list of typed blocks** (`{"text": ...}`, images, documents, tool calls), just like in Anthropic's native API. `converse_stream` exists for streaming, and the Converse API also supports function calling (`toolConfig`) uniformly across models.

**Practical rule: use Converse whenever the model supports it** (all current chat models). This is what the lab `05_bedrock_inference.py` does.

### 3.3 Authentication and IAM

boto3 resolves credentials via the standard chain: environment variables (`AWS_ACCESS_KEY_ID`...), `~/.aws/credentials` profiles (`AWS_PROFILE`), instance/SSO roles. Minimum permissions for inference:

```json
{ "Effect": "Allow",
  "Action": ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream"],
  "Resource": "arn:aws:bedrock:*::foundation-model/*" }
```

In production, restrict the `Resource` to the specific approved models: this is the actual mechanism by which an organization governs "who can use which model".

---

## 4. Bedrock vs. Direct Provider API?

The same Claude family can be consumed via Anthropic's API or via Bedrock. Criteria:

| Factor | Direct Provider API | Bedrock |
|---|---|---|
| Novelties | Models and features on launch day | Usually arrive with a delay |
| Billing | Card/contract per provider | Unified AWS bill (+ credits, + Marketplace) |
| Compliance | Depends on the provider | AWS perimeter: IAM, CloudTrail, PrivateLink, EU regions |
| Multi-model | One integration per provider | One API for all (Converse) |
| Advanced features | All (e.g., full prompt caching) | Subset depending on the model |

Common pattern: prototype with direct APIs (better DX, earlier features) and deploy on Bedrock when the organization demands AWS governance. If you design the model access layer well (a function of yours that encapsulates the call), migrating is cheap.

---

## 5. Common Mistakes

1. **Using the `bedrock` client to infer** (or `bedrock-runtime` to list models). `UnknownOperationException` or nonexistent method: check which client you instantiated.
2. **Not enabling the model in Model access** → `AccessDeniedException` with perfect IAM. Enabled per region: doing it in `us-east-1` does not apply to `eu-west-1`.
3. **Wrong region or model ID without an inference profile.** `ValidationException` or "model not found": check regional availability and if the model requires a `us.`/`eu.` prefix.
4. **Copying `invoke_model` payloads between providers.** Each has its native format; mixing them causes deserialization errors. With Converse, this problem disappears.
5. **Ignoring `stopReason`/`usage`**: same consequences as ignoring `finish_reason` in OpenAI — truncated responses and uncontrolled costs.
6. **AWS credentials in code.** Never: environment variables, profiles, or roles. (And remember: OpenAI/Anthropic keys too — `.env` outside git.)
7. **Setting up SageMaker for something Bedrock already handles.** Start at the highest stack level that covers your use case; only go down when you have a concrete reason.

---

## 6. For Further Reading

- **Amazon Bedrock Documentation**: https://docs.aws.amazon.com/bedrock/
- **Converse API Reference**: https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html
- **boto3, bedrock-runtime client**: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-runtime.html
- **Supported model IDs and inference profiles**: https://docs.aws.amazon.com/bedrock/latest/userguide/models-supported.html
- **Bedrock Pricing** (always check here, do not memorize): https://aws.amazon.com/bedrock/pricing/
- **SageMaker JumpStart**: https://docs.aws.amazon.com/sagemaker/latest/dg/studio-jumpstart.html
- **Amazon Q**: https://aws.amazon.com/q/
- **Claude on Bedrock (Anthropic docs)**: https://docs.anthropic.com/en/api/claude-on-amazon-bedrock
