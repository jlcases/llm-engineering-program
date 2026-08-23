# Guía Dominio 4 — Guidelines for Responsible AI (~14% del examen)

> Dominio conceptual: dimensiones de la IA responsable, bias/fairness, explicabilidad, human oversight y las herramientas AWS asociadas (Bedrock Guardrails, SageMaker Clarify, Model Cards, A2I). Menos servicios, más criterio.

## 1. Dimensiones de Responsible AI

Las que AWS enumera (conviene reconocerlas todas):

- **Fairness**: resultados equitativos entre grupos demográficos; sin discriminación.
- **Explainability**: poder explicar **por qué** el modelo produjo una salida.
- **Transparency**: información abierta sobre qué hace el modelo, sus datos, capacidades y límites (model cards).
- **Privacy & security**: proteger datos personales y del cliente en todo el ciclo.
- **Robustness**: funcionar de forma fiable ante inputs inesperados o adversarios.
- **Governance**: políticas, procesos y auditoría sobre el ciclo de vida de la AI.
- **Veracity / safety**: salidas veraces y no dañinas; controlar hallucinations y contenido tóxico.
- **Controllability**: capacidad de dirigir y limitar el comportamiento del sistema.
- **Human-centricity / accountability**: humanos responsables y en el bucle donde importa.

## 2. Bias (sesgo): tipos y mitigación

- **Origen del bias**: casi siempre **los datos de entrenamiento** (muestras no representativas, prejuicios históricos, etiquetas sesgadas), también decisiones de features y del propio bucle de feedback.
- Tipos que suenan en el examen: **sampling/selection bias** (muestra no representativa), **measurement bias** (mediciones sistemáticamente desviadas), **historical bias** (datos que reflejan discriminación pasada), **confirmation bias** (humano), **algorithmic bias** (amplificado por el modelo).
- **Fairness metrics**: comparar resultados entre subgrupos (p. ej. disparate impact, diferencia de tasas de aprobación).
- Mitigación: datasets **diversos y representativos**, auditorías con **SageMaker Clarify** (pre y post entrenamiento), reequilibrado de datos, monitorización continua en producción, revisión humana en decisiones sensibles (crédito, contratación, salud).
- **Bias-variance** ≠ bias social: no confundir el bias estadístico (underfitting) con el bias de fairness. El examen puede jugar con la palabra.

## 3. Explainability, transparency e interpretabilidad

- **Interpretable model**: se entiende por construcción (linear regression, decision trees).
- **Explainable (post-hoc)**: modelo opaco + técnicas que explican sus salidas (**SHAP**, feature importance) — es lo que hace **SageMaker Clarify**.
- Tradeoff clásico: **modelos más potentes (deep learning, FMs) son menos interpretables**; si el escenario exige justificar cada decisión (regulador, crédito), la respuesta puede ser un modelo interpretable aunque rinda algo menos.
- **Transparencia documental**:
  - **SageMaker Model Cards**: documentación estandarizada del modelo (uso previsto, datos, métricas, limitaciones, consideraciones éticas).
  - **AWS AI Service Cards**: lo mismo pero publicado por AWS para **sus** servicios de AI (Rekognition, Textract...).

## 4. Datasets responsables y human oversight

- Datos: **representatividad**, calidad, consentimiento y licencia, minimización de PII, curación continua (data curation), procedencia documentada.
- **Human-in-the-loop (HITL)**: revisión humana de predicciones — en AWS, **Amazon A2I** (flujos de revisión para predicciones de baja confianza o muestreo aleatorio).
- **SageMaker Ground Truth**: humanos para **etiquetar** datos de entrenamiento (no confundir con A2I, que revisa **inferencias**).
- Decisiones de alto impacto (médicas, legales, financieras) → el examen espera **human oversight**, nunca automatización total.

## 5. Riesgos específicos de generative AI

- **Hallucinations**: mitigar con RAG/grounding, Guardrails (contextual grounding check), revisión humana y comunicación de límites al usuario.
- **Toxicity / contenido dañino**: filtros de contenido (Guardrails), moderación.
- **PII y privacidad**: no enviar datos sensibles innecesarios; redacción de PII.
- **IP/copyright y plagio**: el contenido generado puede parecerse a material protegido.
- **Misuse**: deepfakes, desinformación, fraude.
- **Prompt injection/jailbreak** (cruza con dominios 3 y 5).
- **Legal/reputacional**: responsabilidad por outputs incorrectos; pérdida de confianza del cliente.

## 6. Amazon Bedrock Guardrails (estrella del dominio)

Capa de seguridad configurable **independiente del modelo** (aplica sobre cualquier FM de Bedrock, Agents y Knowledge Bases). Capacidades:

- **Content filters**: umbrales para hate, insults, sexual, violence, misconduct y **prompt attacks** (en input y output).
- **Denied topics**: temas vetados definidos en lenguaje natural (p. ej. "asesoramiento de inversión").
- **Word filters**: palabras/frases bloqueadas (competidores, groserías).
- **Sensitive information filters**: detectar y **bloquear o enmascarar PII** (regex propios incluidos).
- **Contextual grounding checks**: verificar que la respuesta esté fundada en la fuente (anti-hallucination en RAG).
- Nota: Guardrails **filtra/controla contenido en runtime**; no reentrena ni "arregla" el modelo.

## 7. Otras herramientas AWS del dominio

- **SageMaker Clarify**: **detección de bias** (antes y después de entrenar) + **explicabilidad** (SHAP) + evaluación de FMs.
- **SageMaker Model Monitor**: vigila **drift** de datos/calidad del modelo en producción (la calidad responsable se sostiene en el tiempo).
- **Amazon A2I**: revisión humana de predicciones.
- **Model Cards / AI Service Cards**: transparencia documental.

## 8. Trampas típicas del examen

- **Guardrails vs Clarify**: filtrar contenido/PII/temas en un chatbot **en runtime** → **Guardrails**; analizar **bias del dataset/modelo** o explicar predicciones → **Clarify**.
- **Ground Truth vs A2I**: etiquetar datos para entrenar → Ground Truth; revisar predicciones en producción → A2I.
- **Model Cards vs AI Service Cards**: documentas TU modelo → Model Cards; documentación de AWS sobre SUS servicios → AI Service Cards.
- **Model Monitor vs Clarify**: drift en producción → Model Monitor; bias/explicabilidad → Clarify (Clarify también puede monitorizar bias drift vía Model Monitor, pero en el examen la palabra "drift" apunta a Model Monitor).
- **"El modelo discrimina a un grupo" →** revisar/reequilibrar **los datos de entrenamiento** y medir con Clarify; "añadir más capas a la red" es distractor.
- **Interpretabilidad**: si piden "poder explicar cada decisión a un regulador" → modelo interpretable (árbol/lineal) o SHAP/Clarify; no "usar un FM más grande".
- **Hallucinations**: mitigación = grounding/RAG + contextual grounding check + human review; **no** "aumentar temperature" ni "ampliar context window".
- **Fairness ≠ accuracy**: un modelo puede ser muy preciso y aun así injusto con un subgrupo.
- **La automatización total** en decisiones sensibles casi nunca es la opción correcta: busca la respuesta con human oversight.

## 9. Mini-escenarios de repaso (formato examen)

- *"El chatbot de banca no debe hablar de asesoramiento de inversión."* → Guardrails con denied topics.
- *"Hay que enmascarar emails y teléfonos en las respuestas del bot."* → Guardrails con sensitive information filters (PII).
- *"El modelo de crédito aprueba menos solicitudes de un colectivo."* → Medir bias con SageMaker Clarify y reequilibrar los datos de entrenamiento.
- *"El regulador exige explicar por qué se denegó cada solicitud."* → Explicabilidad: SHAP con Clarify, o directamente un modelo interpretable.
- *"Documentar uso previsto, métricas y limitaciones de nuestro modelo."* → SageMaker Model Cards.
- *"Saber las limitaciones que declara AWS sobre Rekognition."* → AWS AI Service Cards.
- *"Las diagnosis del modelo médico deben pasar por un doctor antes de comunicarse."* → Human-in-the-loop con Amazon A2I.
- *"La calidad del modelo cae porque los datos de producción han cambiado."* → SageMaker Model Monitor (drift).
- *"El asistente RAG responde cosas que no están en los documentos."* → Contextual grounding check de Guardrails (+ revisión del retrieval).
- *"Elegir entre un deep model con 95% accuracy y un árbol con 91% para decisiones auditables."* → El interpretable, si el requisito es explicar decisiones.

## 10. Glosario rápido

| Término | Definición de examen |
|---|---|
| Fairness | Resultados equitativos entre grupos |
| Bias (social) | Discriminación sistemática heredada de los datos |
| Sampling bias | Muestra de entrenamiento no representativa |
| Fairness metric | Medida comparando resultados entre subgrupos |
| Explainability | Explicar por qué el modelo dio una salida (post-hoc) |
| Interpretability | El modelo se entiende por construcción |
| SHAP | Técnica de atribución de features para explicar predicciones |
| Transparency | Documentar qué hace el modelo, con qué datos y límites |
| Model Card | Ficha estandarizada de documentación de un modelo |
| HITL | Human-in-the-loop: revisión humana de salidas |
| Toxicity | Contenido dañino/ofensivo generado |
| Contextual grounding | Verificar que la respuesta se apoya en la fuente |
| Denied topic | Tema vetado configurado en Guardrails |
| Veracity | Exactitud factual de las salidas |
| Accountability | Responsabilidad humana asignada sobre el sistema |

## 11. Checklist antes del examen

- [ ] Enumero las dimensiones de Responsible AI (fairness, explainability, transparency, privacy, robustness, governance, safety, controllability).
- [ ] Explico de dónde viene el bias y cómo se mitiga (datos representativos + Clarify + monitorización).
- [ ] Distingo interpretable (por construcción) de explainable (post-hoc, SHAP).
- [ ] Distingo Guardrails (runtime) / Clarify (bias+explicabilidad) / Model Monitor (drift) / A2I (revisión humana).
- [ ] Distingo Model Cards (mi modelo) de AI Service Cards (servicios de AWS).
- [ ] Enumero las 5 capacidades de Bedrock Guardrails.
- [ ] Sé que decisiones de alto impacto requieren human oversight.
- [ ] Identifico los riesgos genAI: hallucinations, toxicity, PII, IP, misuse, prompt attacks.
- [ ] Recuerdo que fairness ≠ accuracy y que el bias estadístico ≠ bias social.

## 12. Cómo leer las preguntas de este dominio

- Si el escenario menciona un **grupo demográfico perjudicado**, la respuesta gira en torno a datos representativos + Clarify, no a cambiar el algoritmo.
- Si menciona **regulador/auditoría/justificar decisiones**, busca explicabilidad (SHAP/Clarify) o modelo interpretable.
- Si menciona **contenido inapropiado/PII/temas prohibidos en un chatbot**, la respuesta es Guardrails.
- Si menciona **decisiones médicas/financieras/legales automatizadas**, la respuesta incluye revisión humana (A2I).
- Si menciona **documentar el modelo**, es Model Cards; si es documentación de AWS sobre sus servicios, AI Service Cards.
- La opción "no hacer nada porque el modelo es preciso" o "automatizar todo" es prácticamente siempre incorrecta en este dominio.
- Cuando dudes entre dos controles, elige el que actúa **más cerca del origen del problema** (datos → training → runtime → revisión humana).

## Mapeo al repo

Este dominio se corresponde con el **módulo 8 (Responsible AI, guardrails, safety en producción)**, con apoyo del módulo 2 (detección de sesgos y alucinaciones).

## Recursos para profundizar

- AWS Responsible AI (página oficial y AI Service Cards publicadas).
- Documentación de Amazon Bedrock Guardrails (capacidades y configuración).
- Documentación de SageMaker Clarify (bias metrics y SHAP).
- Whitepaper/blog de AWS sobre Responsible Use of Machine Learning.
- Curso de AWS Skill Builder: Responsible AI Practices (gratuito).
- NIST AI Risk Management Framework (lectura ligera: basta el resumen ejecutivo).

---

> ⚠️ **Nota**: los contenidos, pesos y servicios citados pueden cambiar. Verifica siempre la **AIF-C01 Exam Guide oficial** en aws.amazon.com/certification antes de presentarte.
