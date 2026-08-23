# Guía Dominio 5 — Security, Compliance, and Governance for AI Solutions (~14% del examen)

> Dominio de "AWS clásico aplicado a AI": asegurar sistemas de AI (IAM, KMS, redes privadas), cumplir normativa (Artifact, Audit Manager, Config) y gobernar los datos. Si vienes de otros exámenes AWS te sonará casi todo; si no, memoriza qué hace cada servicio.

## 1. Modelo de responsabilidad compartida

- **AWS es responsable de la seguridad DE la nube** (infraestructura, hardware, el servicio gestionado en sí).
- **El cliente es responsable de la seguridad EN la nube**: sus datos, configuración de IAM, cifrado activado, prompts y outputs, qué datos envía al modelo.
- Con servicios gestionados como Bedrock, AWS gestiona la infraestructura y los modelos; el cliente sigue siendo responsable de **sus datos, permisos y configuración**.
- Datos en Bedrock: los prompts/completions del cliente **no se usan para entrenar los modelos base** y no se comparten con los proveedores de modelos.

## 2. IAM: identidad y acceso

- **IAM policies**: conceden permisos; principio de **least privilege** (solo lo mínimo necesario, p. ej. permitir `bedrock:InvokeModel` sobre un modelo concreto).
- **IAM roles**: credenciales **temporales** para servicios y aplicaciones (una Lambda que llama a Bedrock debe usar un **rol**, nunca access keys hardcodeadas).
- **IAM users/groups**: personas; MFA recomendado.
- Escenario típico: "la app en EC2/Lambda necesita invocar Bedrock de forma segura" → **IAM role adjunto al servicio**.

### AgentCore Identity y Policy

- **AgentCore Identity** gestiona identidades de workload y credenciales para que un agente acceda
  a AWS o a servicios externos en modo delegado por usuario o autónomo, sin exponer tokens en el
  prompt, el código o los logs.
- **Policy in AgentCore** aplica autorización fina sobre las tools de un AgentCore Gateway mediante
  políticas Cedar: quién puede ejecutar qué acción sobre qué recurso y bajo qué condiciones.
- Distingue autenticación de autorización: Identity demuestra quién es el actor o workload; Policy
  decide si esa identidad puede invocar una tool concreta. Se mantienen mínimo privilegio,
  `default deny` y prevalencia del `forbid` explícito.

## 3. Protección de datos

- **Cifrado at rest**: **AWS KMS** (claves gestionadas por AWS o por el cliente — customer managed keys para control/rotación/auditoría). S3, SageMaker, Bedrock (jobs de customización, Knowledge Bases) cifran con KMS.
- **Cifrado in transit**: TLS/HTTPS en todas las APIs.
- **Amazon Macie**: descubre y clasifica **datos sensibles (PII) en S3** con ML. "¿Hay PII en mis buckets de entrenamiento?" → Macie.
- **Bedrock Guardrails**: enmascara/bloquea PII en prompts y respuestas **en runtime** (Macie = datos almacenados; Guardrails = conversación).
- **Data residency/soberanía**: los datos se quedan en la región elegida; elegir región por requisitos legales (p. ej. GDPR → regiones UE).
- **Data lineage / provenance**: documentar origen y transformaciones de los datos de entrenamiento (gobernanza; cruza con Model Cards).

## 4. Redes privadas

- **VPC endpoints / AWS PrivateLink**: invocar Bedrock, SageMaker o S3 **sin salir a internet público** — el tráfico va por la red de AWS. Escenario: "requisito de que el tráfico al modelo no atraviese internet" → **VPC endpoint (PrivateLink)**.
- SageMaker permite entrenar/desplegar dentro de una VPC sin acceso a internet.

## 5. Auditoría y monitorización

- **AWS CloudTrail**: registra **llamadas a la API** — **quién** hizo **qué** y **cuándo** (p. ej. quién invocó un modelo, quién cambió una configuración). Auditoría y compliance.
- **Amazon CloudWatch**: **métricas, logs y alarmas** de rendimiento operativo (invocaciones, latencia, errores, costes por métrica).
- Regla de oro del examen: **auditoría de acciones → CloudTrail; monitorización de rendimiento → CloudWatch**.
- **Bedrock model invocation logging**: opcional, guarda prompts y respuestas en S3/CloudWatch para auditoría interna.
- **AWS Config**: evalúa **configuración** de recursos contra reglas (p. ej. "todo bucket cifrado"); historial de cambios de configuración.
- **Amazon Inspector**: escanea **vulnerabilidades** en EC2, ECR y Lambda.
- **Amazon GuardDuty**: detección de **amenazas** con ML (actividad anómala en cuentas y cargas).
- **AWS Security Hub**: agrega hallazgos de seguridad (Inspector, GuardDuty, Macie...) en un panel central.

## 6. Compliance y gobernanza

- **AWS Artifact**: **descarga de informes de compliance de AWS** (SOC 2, ISO 27001, PCI...) — evidencia para tus auditores sobre AWS.
- **AWS Audit Manager**: **automatiza la recolección de evidencias** de TUS recursos contra frameworks (GDPR, HIPAA, PCI...) de forma continua.
- Trampa clásica: Artifact = informes **de AWS**; Audit Manager = evidencias **de tu cuenta**.
- **Gobernanza de AI**: políticas internas de uso aceptable, inventario de modelos, revisión de riesgos, comités, documentación (Model Cards), monitorización del ciclo de vida completo.
- Marcos que pueden nombrar (basta reconocerlos): **NIST AI Risk Management Framework**, **ISO/IEC 42001**, **EU AI Act**, OECD AI Principles; y de datos: **GDPR**, **HIPAA** (salud, EE. UU.), **PCI DSS** (pagos).
- **Generative AI Security Scoping Matrix** de AWS: clasifica el nivel de responsabilidad según uses una app de terceros, un servicio gestionado o un modelo propio (más control = más responsabilidad de seguridad).

## 7. Riesgos de seguridad específicos de AI

- **Prompt injection / jailbreak**: mitigar con Guardrails, validación de inputs, least privilege en tools de agentes.
- **Data poisoning**: contaminar datos de entrenamiento → controlar procedencia y acceso a los datasets.
- **Model inversion / membership inference**: extraer información de entrenamiento del modelo → minimizar datos sensibles en el training.
- **Exfiltración vía outputs**: el modelo revela PII o secretos → filtros de salida, logging, revisión.
- **OWASP Top 10 for LLM Applications**: catálogo de riesgos (prompt injection es el nº 1); reconocer el nombre.

## 8. Trampas típicas del examen

- **CloudTrail vs CloudWatch**: "saber quién borró el modelo / auditar llamadas API" → CloudTrail; "alertar si la latencia sube" → CloudWatch.
- **Macie vs Inspector vs GuardDuty**: PII en **S3** → Macie; **vulnerabilidades** de software → Inspector; **amenazas/actividad maliciosa** → GuardDuty.
- **Artifact vs Audit Manager**: informes de compliance **de AWS** → Artifact; recolectar evidencia **de tus recursos** → Audit Manager.
- **Config vs CloudTrail**: estado/cambios de **configuración** contra reglas → Config; registro de **llamadas API** → CloudTrail.
- **KMS vs IAM**: cifrado de datos → KMS; permisos de acceso → IAM. (Ambos suelen aparecer juntos como respuesta "defense in depth".)
- **Roles vs access keys**: cualquier opción con credenciales hardcodeadas es incorrecta; la respuesta es **IAM role** (credenciales temporales).
- **PrivateLink/VPC endpoint**: aparece cuando el requisito es "sin internet público"; un security group o NACL no cumple ese requisito por sí solo.
- **Shared responsibility**: "¿quién parchea la infraestructura de Bedrock?" → AWS; "¿quién configura IAM y cifra sus datos?" → el cliente.
- **Guardrails vs Macie para PII**: conversación en runtime → Guardrails; datos almacenados en S3 → Macie.
- **Least privilege**: ante dos policies válidas, la correcta es siempre la más restrictiva que cumpla el requisito.
- **AgentCore Identity vs Policy**: Identity autentica y gestiona credenciales; Policy autoriza cada tool del Gateway con reglas Cedar.

## 9. Mini-escenarios de repaso (formato examen)

- *"Una Lambda debe invocar Bedrock sin credenciales hardcodeadas."* → IAM role con least privilege.
- *"Auditar qué usuario invocó qué modelo y cuándo."* → AWS CloudTrail.
- *"Alertar si la tasa de errores de invocación supera el 5%."* → CloudWatch alarm.
- *"Comprobar si hay PII en los buckets S3 con datos de entrenamiento."* → Amazon Macie.
- *"El tráfico hacia Bedrock no puede atravesar internet público."* → VPC endpoint (AWS PrivateLink).
- *"Cifrar los datos de fine-tuning con una clave que controle el cliente."* → KMS customer managed key.
- *"El auditor pide el informe SOC 2 de AWS."* → AWS Artifact.
- *"Recolectar evidencia continua de cumplimiento GDPR de nuestros recursos."* → AWS Audit Manager.
- *"Verificar que ningún bucket quede sin cifrado y detectar desvíos de configuración."* → AWS Config.
- *"Detectar actividad anómala/maliciosa en la cuenta."* → Amazon GuardDuty.
- *"Escanear vulnerabilidades en las Lambdas y contenedores de la app de IA."* → Amazon Inspector.
- *"Guardar prompts y respuestas del chatbot para auditoría interna."* → Bedrock model invocation logging (a S3/CloudWatch).
- *"Un agente debe acceder a GitHub en nombre del usuario sin guardar su token."* → AgentCore Identity con acceso delegado.
- *"Solo soporte puede invocar la tool de reembolso y únicamente por debajo de un límite."* → Policy in AgentCore sobre el Gateway.

## 10. Glosario rápido

| Término | Definición de examen |
|---|---|
| Shared responsibility | AWS asegura la nube; el cliente lo que pone en ella |
| Least privilege | Conceder solo los permisos mínimos necesarios |
| IAM role | Identidad con credenciales temporales para servicios |
| KMS | Gestión de claves de cifrado |
| Encryption at rest / in transit | Cifrado almacenado (KMS) / en tránsito (TLS) |
| PrivateLink / VPC endpoint | Acceso privado a servicios AWS sin internet |
| CloudTrail | Registro de llamadas API (quién/qué/cuándo) |
| CloudWatch | Métricas, logs y alarmas operativas |
| AWS Config | Evaluación continua de configuración contra reglas |
| Macie | Descubrimiento de datos sensibles (PII) en S3 |
| GuardDuty | Detección de amenazas |
| Inspector | Escaneo de vulnerabilidades |
| Security Hub | Agregador central de hallazgos de seguridad |
| Artifact | Informes de compliance de AWS bajo demanda |
| Audit Manager | Recolección automática de evidencias de tu cuenta |
| Data lineage | Trazabilidad del origen y transformaciones de los datos |
| Data poisoning | Contaminación maliciosa de datos de entrenamiento |
| OWASP Top 10 for LLM | Catálogo de riesgos de apps LLM (nº1: prompt injection) |
| AgentCore Identity | Identidad y credenciales seguras para agentes y tools |
| Policy in AgentCore | Autorización Cedar por principal, acción, recurso y condiciones |

## 11. Checklist antes del examen

- [ ] Explico shared responsibility aplicado a Bedrock/SageMaker.
- [ ] Sé que los datos de clientes en Bedrock no entrenan los modelos base.
- [ ] Elijo IAM role (nunca keys hardcodeadas) y policies de least privilege.
- [ ] Distingo KMS (cifrado) de IAM (permisos) y sé combinar ambos.
- [ ] Distingo CloudTrail / CloudWatch / Config sin dudar.
- [ ] Distingo Macie / Inspector / GuardDuty / Security Hub.
- [ ] Distingo Artifact (informes de AWS) de Audit Manager (evidencias mías).
- [ ] Sé cuándo la respuesta es VPC endpoint/PrivateLink.
- [ ] Reconozco NIST AI RMF, ISO 42001, EU AI Act, GDPR, HIPAA, PCI DSS.
- [ ] Identifico data poisoning, model inversion y prompt injection con su mitigación.
- [ ] Distingo AgentCore Identity (autenticación/credenciales) de Policy (autorización de tools).

## 12. Cómo leer las preguntas de este dominio

- Identifica el **verbo del requisito**: "auditar quién" → CloudTrail; "alertar/medir" → CloudWatch; "descubrir PII" → Macie; "demostrar compliance de AWS" → Artifact; "recolectar mi evidencia" → Audit Manager; "evaluar configuración" → Config.
- "Sin acceso a internet / tráfico privado" → VPC endpoint (PrivateLink); las opciones con NAT gateway o security groups no cumplen ese requisito por sí solas.
- Cualquier opción con **credenciales embebidas en el código** queda descartada de inmediato.
- Si dos opciones cumplen, gana la de **menor privilegio** o **menor superficie de exposición**.
- En preguntas de shared responsibility, pregúntate: ¿esto lo configura el cliente o lo opera AWS? Lo que el cliente configura (IAM, cifrado de sus datos, sus prompts) siempre es responsabilidad del cliente.
- Los marcos regulatorios se preguntan a nivel de reconocimiento: HIPAA↔salud, PCI DSS↔pagos, GDPR↔datos personales UE, NIST AI RMF/ISO 42001↔gestión de riesgo de AI.

## Mapeo al repo

Este dominio se corresponde con el **módulo 8 (LLMOps: seguridad, IAM, KMS, CloudTrail, VPC endpoints, governance)**.

## Recursos para profundizar

- AWS Well-Architected Framework — Security Pillar (nivel de lectura general).
- Generative AI Security Scoping Matrix (blog de AWS Security).
- Documentación de IAM: policies, roles y least privilege.
- Documentación de Bedrock: data protection y model invocation logging.
- OWASP Top 10 for Large Language Model Applications.
- Curso de AWS Skill Builder: Security, Compliance, and Governance for AI Solutions.

---

> ⚠️ **Nota**: los contenidos, pesos y servicios citados pueden cambiar. Verifica siempre la **AIF-C01 Exam Guide oficial** en aws.amazon.com/certification antes de presentarte.
