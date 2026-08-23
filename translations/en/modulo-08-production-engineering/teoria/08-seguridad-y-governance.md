# 08 — LLM System Security and Governance

> Associated Lab: [`../labs/07_prompt_injection.py`](../labs/07_prompt_injection.py)

An LLM mixes instructions and data in the same probabilistic channel. This property creates new attacks, but most serious impacts still exploit classic failures: excessive permissions, exposed secrets, incomplete authorization, vulnerable dependencies, and the absence of limits.

## 1. Threat Model Before Controls

Assets:

- user data, private corpus, and memories;
- system prompts and internal policies;
- credentials and tool permissions;
- inference/GPU budget;
- integrity of indexes, prompts, and models;
- product availability and reputation.

Actors and inputs:

- authenticated or anonymous user;
- retrieved content: web, email, PDF, issue, repository;
- third-party MCP/tool server;
- compromised dependency, model, or dataset;
- internal operator with legitimate access;
- another tenant attempting data crossing.

Map the trust boundaries. Every external text that reaches the model remains untrusted
even if it comes from your vector DB.

## 2. Direct and Indirect Prompt Injection

- **Direct:** the user attempts to overwrite instructions.
- **Indirect:** a consulted source contains malicious instructions.

Separating with tags and saying "ignore instructions from the document" reduces success, but does not prove
isolation. Strong controls:

1. minimize available tools and privileges;
2. separate read from write and confirmation;
3. validate arguments, entity, tenant, and policy outside the model;
4. do not pass secrets into the context;
5. allowlist of destinations/operations;
6. sandbox for code or active content;
7. monitor trajectories and cut off by budget;
8. continuous adversarial testing.

The model must not decide whether a user can close an account. It may propose the action; a
policy engine checks identity and permissions and authorizes or denies.

## 3. Excessive agency

The risk grows with four factors:

```text
impacto ≈ autonomía × privilegio × alcance × irreversibilidad
```

Reduce each one:

- autonomy: approval or deterministic workflow;
- privilege: narrow and temporary token/role;
- scope: specific tools, filters, and limits;
- irreversibility: draft, dry-run, trash, transaction, and compensation.

A tool `send_email(to, body)` is riskier than `draft_reply(ticket_id)`. The second leaves the
effect to a system with authorization and review.

## 4. Authentication is not authorization

In each tool, validate:

- identity and tenant of the request;
- permission on the action;
- permission on the specific object;
- state that allows the transition;
- valid confirmation linked to those arguments;
- rate/budget limit;
- idempotency key for writes.

Do not accept `tenant_id` from the model as the source of truth. Derive it from the authenticated token/session and
apply it in the DB, vector search, cache, logs, and storage.

## 5. Data and Secret Leakage

Never introduce credentials into prompts. The LLM does not need the API token: the tool uses it on the server. Draft:

- Authorization headers and cookies;
- environment variables;
- tokens in URLs;
- unnecessary PII;
- out-of-scope DB results;
- system prompts if their exposure increases operational risk.

Hiding the system prompt is not a security boundary: assume that part of it can be inferred. Guarantees must survive its disclosure.

Mitigate mass extraction with pagination, limits, filters, pattern detection, and egress control.

## 6. RAG Security

Threats:

- corpus or metadata poisoning;
- tenant cross-over due to missing filters;
- indirect injection;
- obsolete documents displacing policies;
- exfiltrated embeddings/index;
- active URLs or attachments returned to the user.

Controls:

- authenticated ingestion, review, and signature/provenance;
- namespaces and server-side filters;
- versioning, validity, and index rollback;
- content/file scanning;
- citations with allowed IDs;
- negative isolation tests;
- do not render active HTML/Markdown without sanitization.

## 7. Supply Chain

The stack includes packages, images, models, adapters, datasets, remote prompts, MCP servers, and plugins. Apply:

- lockfiles and hashes/digests;
- SBOM and dependency/image scanning;
- minimal and non-root base images;
- license and weight/data provenance verification;
- fixed versions of MCP servers;
- review of changes in tool descriptions;
- separation of build and runtime;
- signing/attestation when risk requires it.

A downloaded model executes loading code in some ecosystems; use secure formats,
`trust_remote_code=False` except for review and isolated environments.

## 8. Denial of Wallet and Availability

An attacker can multiply tokens, steps, searches, and tool calls. Limit:

- input/document size;
- output tokens;
- iterations and tools per task;
- concurrency per user/tenant;
- cost per request/day;
- recursion depth and multi-agent fan-out;
- time and size of results;
- retries.

Use rate limits, quotas, circuit breakers, secure caching, and queues with backpressure. Alert on cost
and tokens, not just CPU.

## 9. Generated Code and Sandbox

If you execute model-generated code:

- ephemeral container/VM without privileges;
- temporary and read-only filesystem where possible;
- no network or with an egress allowlist;
- CPU/memory/time/process limits;
- no Docker socket mounting or credentials;
- validation of artifacts before returning them;
- complete destruction of the environment.

A regex that blocks `rm` is not a sandbox. Languages have multiple equivalent pathways.

## 10. AWS Controls

### IAM

- roles based on workload and environment;
- specific actions/resources and conditions;
- temporary credentials;
- SCP/permission boundaries for organizational limits;
- Access Analyzer for policies and external access.

### Encryption and Secrets

- KMS with key separation and policies;
- Secrets Manager with rotation where applicable;
- TLS in transit;
- do not store secrets in env dumps/logs/images.

### Network and Audit

- private subnets and minimal security groups;
- VPC endpoints for supported services;
- WAF/rate limiting;
- CloudTrail for API/control plane;
- Config for configuration drift;
- GuardDuty/Security Hub for findings;
- Macie for sensitive data in S3.

### Governance

- AWS Artifact: AWS compliance reports;
- Audit Manager: collect evidence of your controls;
- Organizations/Control Tower: multi-account guardrails;
- tagging and separate accounts by environment.

## 11. Secure Logging

Log necessary events without copying the full payload by default:

```json
{
  "trace_id": "tr-9f2a",
  "tenant_hash": "t-73b1",
  "tool": "close_incident",
  "policy_decision": "denied",
  "reason_code": "confirmation_missing",
  "arguments_hash": "sha256:7c04",
  "latency_ms": 18,
  "prompt_version": "agent-4.2.0"
}
```

Control access, retention, and integrity. LLM traces can contain more sensitivity than traditional web logs.

## 12. Red-teaming and Incident Response

Test attacks tailored to your tools and data, not just a generic list:

- injection in every source;
- encoding/languages and hidden text;
- extraction via small iterations;
- tenant/ID confusion;
- malicious tool outputs;
- abuse of retries and parallelism;
- prompt/model/MCP server switching;
- duplicate side effects.

Incident plan:

1. disable tool/alias/model or set read-only mode;
2. revoke credentials;
3. preserve redacted evidence;
4. identify affected sessions/data;
5. fix root control and add case to dataset;
6. communicate per obligations;
7. verify recovery and document postmortem.

## Common mistakes

1. Relying on the system prompt as an authorization control.
2. Passing secrets to the model and asking it not to reveal them.
3. Filtering tenant after retrieving results.
4. Providing generic tools with powerful credentials.
5. Executing code on the same host as the application.
6. Logging full prompts without a data policy.
7. Not limiting cost and steps per task.

## To go deeper

- OWASP GenAI Security Project: https://genai.owasp.org/
- MITRE ATLAS: https://atlas.mitre.org/
- AWS, Security in Amazon Bedrock: https://docs.aws.amazon.com/bedrock/latest/userguide/security.html
- NIST AI RMF: https://www.nist.gov/itl/ai-risk-management-framework
