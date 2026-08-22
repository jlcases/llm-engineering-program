# Domain 5 Guide — Security, Compliance, and Governance for AI Solutions (~14% of the exam)

> "Classic AWS applied to AI" domain: securing AI systems (IAM, KMS, private networks), ensuring compliance (Artifact, Audit Manager, Config), and governing data. If you're coming from other AWS exams, almost everything will sound familiar; if not, memorize what each service does.

## 1. Shared Responsibility Model

- **AWS is responsible for security OF the cloud** (infrastructure, hardware, the managed service itself).
- **The customer is responsible for security IN the cloud**: their data, IAM configuration, encryption enabled, prompts and outputs, and what data they send to the model.
- With managed services like Bedrock, AWS manages the infrastructure and models; the customer remains responsible for **their data, permissions, and configuration**.
- Data in Bedrock: customer prompts/completions **are not used to train base models** and are not shared with model providers.

## 2. IAM: Identity and Access

- **IAM policies**: grant permissions; follow the **least privilege** principle (only what is strictly necessary, e.g., allowing `bedrock:InvokeModel` on a specific model).
- **IAM roles**: **temporary** credentials for services and applications (a Lambda calling Bedrock must use an **IAM role**, never hardcoded access keys).
- **IAM users/groups**: people; MFA recommended.
- Typical scenario: "the app on EC2/Lambda needs to invoke Bedrock securely" → **IAM role attached to the service**.

### AgentCore Identity and Policy

- **AgentCore Identity** manages workload identities and credentials so an agent can access AWS or external services in user-delegated or autonomous mode, without exposing tokens in prompts, code, or logs.
- **Policy in AgentCore** applies fine-grained authorization over the tools of an AgentCore Gateway using Cedar policies: who can execute what action on what resource and under which conditions.
- Distinguish authentication from authorization: Identity proves who the actor or workload is; Policy decides whether that identity can invoke a specific tool. Maintain least privilege, `default deny`, and the explicit precedence of `forbid`.

## 3. Data Protection

- **Encryption at rest**: **AWS KMS** (AWS-managed or customer-managed keys — customer managed keys for control/rotation/auditing). S3, SageMaker, Bedrock (customization jobs, Knowledge Bases) encrypt with KMS.
- **Encryption in transit**: TLS/HTTPS across all APIs.
- **Amazon Macie**: discovers and classifies **sensitive data (PII) in S3** using ML. "Is there PII in my training buckets?" → Macie.
- **Bedrock Guardrails**: masks/blocks PII in prompts and responses **at runtime** (Macie = stored data; Guardrails = conversation).
- **Data residency/sovereignty**: data remains in the chosen region; select a region based on legal requirements (e.g., GDPR → EU regions).
- **Data lineage / provenance**: document the origin and transformations of training data (governance; cross-references with Model Cards).

## 4. Private Networks

- **VPC endpoints / AWS PrivateLink**: invoke Bedrock, SageMaker, or S3 **without traversing the public internet** — traffic stays within the AWS network. Scenario: "requirement that model traffic must not cross the internet" → **VPC endpoint (PrivateLink)**.
- SageMaker allows training/deploying within a VPC without internet access.

## 5. Auditing and Monitoring

- **AWS CloudTrail**: logs **API calls** — **who** did **what** and **when** (e.g., who invoked a model, who changed a configuration). Auditing and compliance.
- **Amazon CloudWatch**: **metrics, logs, and alarms** for operational performance (invocations, latency, errors, costs per metric).
- Exam golden rule: **action auditing → CloudTrail; performance monitoring → CloudWatch**.
- **Bedrock model invocation logging**: optional, saves prompts and responses to S3/CloudWatch for internal auditing.
- **AWS Config**: evaluates resource **configuration** against rules (e.g., "all buckets encrypted"); tracks configuration change history.
- **Amazon Inspector**: scans for **vulnerabilities** in EC2, ECR, and Lambda.
- **Amazon GuardDuty**: **threat detection** using ML (anomalous activity in accounts and workloads).
- **AWS Security Hub**: aggregates security findings (Inspector, GuardDuty, Macie...) into a central dashboard.

## 6. Compliance and Governance

- **AWS Artifact**: **downloads AWS compliance reports** (SOC 2, ISO 27001, PCI...) — evidence for your auditors regarding AWS.
- **AWS Audit Manager**: **automates the collection of evidence** from YOUR resources against frameworks (GDPR, HIPAA, PCI...) continuously.
- Classic trap: Artifact = reports **from AWS**; Audit Manager = evidence **from your account**.
- **AI Governance**: internal acceptable use policies, model inventory, risk reviews, committees, documentation (Model Cards), full lifecycle monitoring.
- Frameworks you may be asked to recognize (just recognizing them is enough): **NIST AI Risk Management Framework**, **ISO/IEC 42001**, **EU AI Act**, OECD AI Principles; and data frameworks: **GDPR**, **HIPAA** (healthcare, US), **PCI DSS** (payments).
- AWS **Generative AI Security Scoping Matrix**: classifies the level of responsibility based on whether you use a third-party app, a managed service, or a custom model (more control = more security responsibility).

## 7. AI-Specific Security Risks

- **Prompt injection / jailbreak**: mitigate with Guardrails, input validation, least privilege on agent tools.
- **Data poisoning**: contaminate training data → control provenance and access to datasets.
- **Model inversion / membership inference**: extract training information from the model → minimize sensitive data in training.
- **Exfiltration via outputs**: model reveals PII or secrets → output filters, logging, review.
- **OWASP Top 10 for LLM Applications**: risk catalog (prompt injection is #1); recognize the name.

## 8. Typical Exam Traps

- **CloudTrail vs CloudWatch**: "know who deleted the model / audit API calls" → CloudTrail; "alert if latency increases" → CloudWatch.
- **Macie vs Inspector vs GuardDuty**: PII in **S3** → Macie; software **vulnerabilities** → Inspector; **threats/malicious activity** → GuardDuty.
- **Artifact vs Audit Manager**: compliance reports **from AWS** → Artifact; collect evidence **from your resources** → Audit Manager.
- **Config vs CloudTrail**: state/changes of **configuration** against rules → Config; log of **API calls** → CloudTrail.
- **KMS vs IAM**: data encryption → KMS; access permissions → IAM. (Both often appear together as a "defense in depth" answer.)
- **Roles vs access keys**: any option with hardcoded credentials is incorrect; the answer is an **IAM role** (temporary credentials).
- **PrivateLink/VPC endpoint**: appears when the requirement is "no public internet"; a security group or NACL alone does not meet that requirement.
- **Shared responsibility**: "who patches Bedrock infrastructure?" → AWS; "who configures IAM and encrypts their data?" → the customer.
- **Guardrails vs Macie for PII**: conversation at runtime → Guardrails; data stored in S3 → Macie.
- **Least privilege**: when two valid policies exist, the correct one is always the most restrictive that fulfills the requirement.
- **AgentCore Identity vs Policy**: Identity authenticates and manages credentials; Policy authorizes each Gateway tool with Cedar rules.

## 9. Mini Review Scenarios (Exam Format)

- *"A Lambda must invoke Bedrock without hardcoded credentials."* → IAM role with least privilege.
- *"Audit which user invoked which model and when."* → AWS CloudTrail.
- *"Alert if the invocation error rate exceeds 5%."* → CloudWatch alarm.
- *"Check if there is PII in the S3 buckets with training data."* → Amazon Macie.
- *"Traffic to Bedrock cannot traverse the public internet."* → VPC endpoint (AWS PrivateLink).
- *"Encrypt fine-tuning data with a key controlled by the customer."* → KMS customer managed key.
- *"The auditor requests the SOC 2 report from AWS."* → AWS Artifact.
- *"Collect continuous GDPR compliance evidence from our resources."* → AWS Audit Manager.
- *"Verify that no bucket is unencrypted and detect configuration drift."* → AWS Config.
- *"Detect anomalous/malicious activity in the account."* → Amazon GuardDuty.
- *"Scan for vulnerabilities in the AI app's Lambdas and containers."* → Amazon Inspector.
- *"Save chatbot prompts and responses for internal auditing."* → Bedrock model invocation logging (to S3/CloudWatch).
- *"An agent must access GitHub on behalf of the user without saving its token."* → AgentCore Identity with delegated access.
- *"Only support can invoke the refund tool and only below a certain limit."* → Policy in AgentCore on the Gateway.

## 10. Quick Glossary

| Term | Exam Definition |
|---|---|
| Shared responsibility | AWS secures the cloud; the customer secures what they put in it |
| Least privilege | Grant only the minimum necessary permissions |
| IAM role | Identity with temporary credentials for services |
| KMS | Encryption key management |
| Encryption at rest / in transit | Stored encryption (KMS) / transit encryption (TLS) |
| PrivateLink / VPC endpoint | Private access to AWS services without internet |
| CloudTrail | API call logging (who/what/when) |
| CloudWatch | Operational metrics, logs, and alarms |
| AWS Config | Continuous configuration evaluation against rules |
| Macie | Discovery of sensitive data (PII) in S3 |
| GuardDuty | Threat detection |
| Inspector | Vulnerability scanning |
| Security Hub | Central aggregator of security findings |
| Artifact | On-demand AWS compliance reports |
| Audit Manager | Automatic collection of account evidence |
| Data lineage | Traceability of data origin and transformations |
| Data poisoning | Malicious contamination of training data |
| OWASP Top 10 for LLM | LLM app risk catalog (#1: prompt injection) |
| AgentCore Identity | Secure identity and credentials for agents and tools |
| Policy in AgentCore | Cedar authorization by principal, action, resource, and conditions |

## 11. Pre-Exam Checklist

- [ ] You explain shared responsibility applied to Bedrock/SageMaker.
- [ ] You know that customer data in Bedrock does not train base models.
- [ ] You select IAM roles (never hardcoded keys) and least privilege policies.
- [ ] You distinguish KMS (encryption) from IAM (permissions) and know how to combine both.
- [ ] You distinguish CloudTrail / CloudWatch / Config without hesitation.
- [ ] You distinguish Macie / Inspector / GuardDuty / Security Hub.
- [ ] You distinguish Artifact (AWS reports) from Audit Manager (your evidence).
- [ ] You know when the answer is VPC endpoint/PrivateLink.
- [ ] You recognize NIST AI RMF, ISO 42001, EU AI Act, GDPR, HIPAA, PCI DSS.
- [ ] You identify data poisoning, model inversion, and prompt injection with their mitigations.
- [ ] You distinguish AgentCore Identity (authentication/credentials) from Policy (tool authorization).

## 12. How to Read Questions in This Domain

- Identify the **requirement verb**: "audit who" → CloudTrail; "alert/measure" → CloudWatch; "discover PII" → Macie; "demonstrate AWS compliance" → Artifact; "collect my evidence" → Audit Manager; "evaluate configuration" → Config.
- "No internet access / private traffic" → VPC endpoint (PrivateLink); options with NAT gateway or security groups do not meet that requirement on their own.
- Any option with **credentials embedded in code** is immediately disqualified.
- If two options work, the one with **least privilege** or **smallest attack surface** wins.
- For shared responsibility questions, ask yourself: does the customer configure this or does AWS operate it? What the customer configures (IAM, encryption of their data, their prompts) is always the customer's responsibility.
- Regulatory frameworks are tested at a recognition level: HIPAA↔healthcare, PCI DSS↔payments, GDPR↔EU personal data, NIST AI RMF/ISO 42001↔AI risk management.

## Repo Mapping

This domain corresponds to **module 5 (LLMOps: security, IAM, KMS, CloudTrail, VPC endpoints, governance)**.

## Resources for Further Study

- AWS Well-Architected Framework — Security Pillar (general reading level).
- Generative AI Security Scoping Matrix (AWS Security blog).
- IAM documentation: policies, roles, and least privilege.
- Bedrock documentation: data protection and model invocation logging.
- OWASP Top 10 for Large Language Model Applications.
- AWS Skill Builder course: Security, Compliance, and Governance for AI Solutions.

---

> ⚠️ **Note**: the content, weights, and services cited may change. Always verify the official **AIF-C01 Exam Guide** at aws.amazon.com/certification before taking the exam.
