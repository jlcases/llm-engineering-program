# Flashcards AWS Certified AI Practitioner (AIF-C01)

> Flashcards agrupadas por los 5 dominios de la revisión 1.1. Formato pregunta → respuesta: tapa la respuesta, contesta en voz alta y comprueba. Los pesos y el temario pueden cambiar: verifica la **exam guide oficial** antes de presentarte.

---

## Dominio 1 — Fundamentals of AI and ML

**P:** ¿Cuál es la relación entre AI, ML y deep learning?
**R:** Deep learning ⊂ machine learning ⊂ inteligencia artificial. El DL usa redes neuronales profundas; el ML aprende patrones de datos; la IA es el campo general.

**P:** ¿Qué diferencia al aprendizaje supervisado del no supervisado?
**R:** El supervisado entrena con datos **etiquetados** (clasificación, regresión); el no supervisado encuentra estructura en datos **sin etiquetas** (clustering, reducción de dimensionalidad).

**P:** ¿Qué es el aprendizaje por refuerzo (reinforcement learning)?
**R:** Un agente aprende por prueba y error interactuando con un entorno y maximizando una señal de recompensa. No usa dataset etiquetado.

**P:** ¿Clasificación vs regresión?
**R:** Clasificación predice una **categoría** (spam/no spam); regresión predice un **valor continuo** (precio, demanda).

**P:** ¿Qué es el overfitting y cómo se mitiga?
**R:** El modelo memoriza el train y generaliza mal (train alto, test bajo). Mitigación: más datos, regularización, modelos más simples, early stopping.

**P:** ¿Por qué la accuracy engaña con clases desbalanceadas y qué métricas usar?
**R:** Un modelo que siempre predice la clase mayoritaria "acierta" casi todo. Usa precision, recall y F1; recall si el falso negativo es lo caro (fraude, enfermedad).

**P:** ¿Precision vs recall?
**R:** Precision: de lo que marqué positivo, cuánto era realmente positivo. Recall: de todos los positivos reales, cuántos capturé.

**P:** ¿Batch inference vs real-time inference?
**R:** Batch: predicciones masivas periódicas, sin urgencia, más barato. Real-time: endpoint siempre activo con respuesta inmediata, más caro.

**P:** ¿Qué es feature engineering?
**R:** Crear/transformar variables de entrada a partir de datos crudos para que el modelo aprenda mejor (normalización, encoding, agregados…).

**P:** ¿Qué hace Amazon Textract?
**R:** Extrae texto, tablas y pares clave-valor de documentos escaneados (OCR inteligente). Documentos, no fotos generales.

**P:** ¿Qué hace Amazon Comprehend?
**R:** NLP gestionado sobre texto: sentimiento, entidades, key phrases, idioma y detección de PII.

**P:** ¿Qué hace Amazon Rekognition?
**R:** Visión por computador en imágenes y vídeo: objetos, escenas, caras, texto en imagen y moderación de contenido.

**P:** ¿Polly vs Transcribe?
**R:** Polly: texto → voz (TTS). Transcribe: voz → texto (STT). Son inversos.

**P:** ¿Qué es Amazon SageMaker AI en una frase?
**R:** La plataforma gestionada para construir, entrenar, evaluar y desplegar modelos de ML **propios** de extremo a extremo.

**P:** ¿Cuándo NO usar ML?
**R:** Cuando el problema se resuelve con reglas deterministas simples y estables (cálculos fiscales, validaciones), o no hay datos suficientes.

---

## Dominio 2 — Fundamentals of Generative AI

**P:** ¿Qué es un foundation model?
**R:** Modelo grande pre-entrenado con datos masivos (normalmente auto-supervisado) que se adapta a muchas tareas vía prompting, RAG o fine-tuning.

**P:** ¿Qué es un token y qué es la context window?
**R:** El token es la unidad mínima de texto que procesa el modelo (~subpalabras). La context window es el máximo de tokens de entrada+salida por petición.

**P:** ¿Qué son los embeddings?
**R:** Vectores numéricos que representan el significado de un texto (o imagen); textos similares quedan cerca en el espacio vectorial → búsqueda semántica.

**P:** ¿Qué controla la temperatura?
**R:** La aleatoriedad del muestreo: baja → salidas más deterministas/repetibles; alta → más diversas/creativas.

**P:** ¿Temperature vs top_p vs top_k?
**R:** Los tres regulan el muestreo: temperature reescala probabilidades; top_p limita al núcleo de probabilidad acumulada; top_k limita a los k tokens más probables.

**P:** ¿Qué controla max tokens?
**R:** Solo la **longitud máxima** de la salida. No afecta a la creatividad ni a la calidad.

**P:** ¿Qué es una alucinación?
**R:** Contenido inventado pero plausible presentado con seguridad. Mitigación: RAG/grounding, temperatura baja, guardrails, revisión humana.

**P:** Orden de menor a mayor coste para adaptar un FM:
**R:** Prompt engineering → RAG → fine-tuning → continued pre-training → entrenar desde cero.

**P:** ¿Fine-tuning vs continued pre-training?
**R:** Fine-tuning: datos **etiquetados** (pares prompt-respuesta) para tarea/estilo. Continued pre-training: corpus **sin etiquetar** para absorber lenguaje de dominio.

**P:** ¿Zero-shot vs few-shot?
**R:** Zero-shot: solo instrucciones. Few-shot: se incluyen ejemplos resueltos en el prompt (in-context learning, sin cambiar pesos).

**P:** ¿Qué es Amazon Bedrock?
**R:** Servicio serverless que da acceso por API unificada a foundation models de Amazon y terceros (Anthropic, Meta, Mistral…), con customización, Agents, Knowledge Bases y Guardrails.

**P:** ¿Qué es Amazon Q Business?
**R:** Asistente de IA generativa gestionado para empleados: se conecta a datos corporativos (S3, SharePoint, Salesforce…) respetando permisos. Q Developer es su hermano para código/AWS.

**P:** ¿Qué es Amazon Quick?
**R:** Workspace gestionado de IA para chat, agentes, BI/visualización, investigación y automatización sobre datos y aplicaciones conectadas. Amazon Quick Sight es la capacidad de business intelligence dentro de Quick.

**P:** ¿Qué es Kiro en el alcance AIF-C01?
**R:** Un IDE agéntico para desarrollo guiado por especificaciones, steering files y hooks que automatizan controles de calidad.

**P:** ¿Qué es Strands Agents?
**R:** SDK open source y model-first para construir agentes con tools, múltiples proveedores y protocolos como MCP. Es código/framework, no el hosting gestionado.

**P:** ¿Qué es Amazon Bedrock AgentCore?
**R:** Infraestructura model- y framework-agnostic para desplegar y operar agentes: Runtime, Gateway, Memory, Identity, Observability, Evaluations y Policy.

**P:** ¿Strands Agents vs AgentCore?
**R:** Strands construye la lógica del agente; AgentCore puede alojar y operar agentes de Strands, LangGraph, CrewAI o código propio con servicios gestionados.

**P:** ¿Qué aporta AgentCore Identity?
**R:** Identidad de workload y gestión segura de credenciales para que agentes y tools accedan a AWS o terceros, con autenticación, autorización y traza auditable.

**P:** ¿Qué es model distillation?
**R:** Entrenar un modelo menor para imitar el comportamiento de uno mayor; busca conservar calidad útil reduciendo coste y latencia.

**P:** ¿On-demand vs Provisioned Throughput en Bedrock?
**R:** On-demand: pago por token, tráfico variable. Provisioned: capacidad reservada, coste estable y throughput garantizado; necesario para servir modelos customizados.

**P:** ¿Qué métrica se asocia a resúmenes y cuál a traducción?
**R:** ROUGE para summarization; BLEU para traducción. Ambas comparan con textos de referencia.

**P:** ¿Qué es el knowledge cutoff?
**R:** La fecha límite de los datos de entrenamiento: el modelo no conoce hechos posteriores. Se compensa con RAG o herramientas.

**P:** ¿Qué es un modelo multimodal?
**R:** El que acepta y/o genera varias modalidades (texto, imagen, audio) en la misma petición.

**P:** ¿Prompt engineering vs context engineering?
**R:** Prompt engineering diseña instrucciones y ejemplos. Context engineering compone además historial, memoria, documentos RAG, resultados de tools y metadatos dentro de la ventana y del presupuesto de tokens.

**P:** ¿Qué aporta MCP a un sistema agéntico?
**R:** Una interfaz estándar para descubrir y usar tools, recursos y contexto de sistemas externos. MCP conecta; la orquestación decide la secuencia, el estado, los reintentos y las aprobaciones.

**P:** ¿Cuándo compensa un sistema multi-agent?
**R:** Cuando la especialización, delegación o revisión entre agentes aporta más que su coste, latencia y complejidad. Para una tarea lineal, un solo agente suele ser mejor.

---

## Dominio 3 — Applications of Foundation Models

**P:** ¿Qué es RAG y cuándo elegirlo?
**R:** Retrieval-Augmented Generation: recuperar fragmentos relevantes de tus datos e inyectarlos en el prompt. Elígelo cuando el conocimiento cambia a menudo o debe citarse, sin reentrenar.

**P:** ¿Qué hace Bedrock Knowledge Bases?
**R:** RAG gestionado: ingestión desde S3, chunking, embeddings, almacén vectorial (p. ej. OpenSearch Serverless) y APIs de retrieve/retrieve-and-generate.

**P:** ¿Qué es el chunking y por qué importa?
**R:** Trocear documentos antes de generar embeddings. Chunks bien dimensionados → retrieval más preciso y contexto que cabe en la ventana del modelo.

**P:** Nombra dos opciones de almacén vectorial en AWS.
**R:** La guía 1.1 cita Amazon OpenSearch Service, Aurora, Neptune y Amazon RDS for PostgreSQL; pgvector es el mecanismo habitual en PostgreSQL.

**P:** ¿Qué hace Bedrock Agents?
**R:** Orquesta tareas multi-paso: el modelo planifica, llama APIs definidas en **action groups**, consulta knowledge bases y devuelve el resultado.

**P:** ¿Knowledge Bases vs Agents: cuándo cada uno?
**R:** Solo responder preguntas sobre documentos → Knowledge Bases. Ejecutar acciones contra APIs (crear tickets, pedidos) → Agents (que pueden incluir una KB).

**P:** ¿Qué es chain-of-thought prompting?
**R:** Pedir razonamiento paso a paso antes de la respuesta final; mejora tareas de lógica y varios pasos.

**P:** ¿Qué hace Amazon Bedrock Prompt Management?
**R:** Permite crear, probar, guardar, versionar y reutilizar prompts y variantes. Cada versión debe evaluarse con un dataset estable y conservar una ruta de rollback.

**P:** ¿Qué es prompt injection y cómo se mitiga?
**R:** Entrada de usuario que intenta anular las instrucciones del sistema ("ignora tus instrucciones…"). Mitigación: guardrails, separar instrucciones de datos, validar entradas, mínimo privilegio en tools.

**P:** ¿Qué hace Bedrock Guardrails?
**R:** Filtra en inferencia: denied topics, contenido dañino, PII (bloqueo o enmascarado), word filters y detección de grounding contextual. Aplica a entrada y salida.

**P:** ¿Qué es Bedrock Model Evaluation?
**R:** Comparar FMs con métricas automáticas (accuracy, robustness, toxicity) o evaluación humana sobre datasets propios, para elegir modelo.

**P:** Criterios para elegir un foundation model:
**R:** Modalidades, calidad en la tarea, tamaño de context window, coste por token, latencia, idiomas, opciones de customización y licencia.

**P:** ¿Cuándo elegir fine-tuning en lugar de RAG?
**R:** Cuando quieres fijar **estilo/formato/comportamiento** con muchos ejemplos etiquetados. RAG cuando el problema es **conocimiento** actualizado o citable.

**P:** ¿Qué son las stop sequences?
**R:** Cadenas que, al generarse, detienen la salida. Sirven para delimitar formatos y evitar texto de más.

**P:** Buenas prácticas de prompt para RAG:
**R:** Delimitar el contexto recuperado, ordenar "responde solo con este contexto", pedir "di que no lo sabes" si falta información, y pedir citas.

**P:** ¿Qué pasa con tus datos al customizar un modelo en Bedrock?
**R:** Quedan privados: se crea una copia del modelo para tu cuenta y tus datos no se usan para mejorar los modelos base.

**P:** ¿Qué es la inferencia con menor modelo suficiente (right-sizing)?
**R:** Usar el modelo más pequeño que cumpla la calidad requerida: menos coste y latencia. No usar el más grande "por si acaso".

---

## Dominio 4 — Guidelines for Responsible AI

**P:** Dimensiones típicas de Responsible AI:
**R:** Fairness, explicabilidad, transparencia, privacidad y seguridad, robustez, gobernanza, controlabilidad y veracidad.

**P:** ¿Qué es fairness?
**R:** Que el sistema no produzca resultados sistemáticamente peores para grupos protegidos (género, edad, etnia…).

**P:** ¿Cuál es la fuente más común de sesgo en un modelo?
**R:** Datos de entrenamiento sesgados o no representativos: el modelo reproduce la discriminación presente en el histórico.

**P:** ¿Qué hace SageMaker Clarify?
**R:** Detecta sesgo en datos y modelos (pre y post entrenamiento) y explica predicciones con feature attributions (SHAP).

**P:** ¿Guardrails vs Clarify?
**R:** Guardrails filtra contenido en **inferencia** (temas, toxicidad, PII). Clarify analiza **sesgo y explicabilidad** en el ciclo de ML. No compiten: se complementan.

**P:** ¿Qué es Amazon A2I (Augmented AI)?
**R:** Servicio para insertar **revisión humana** en flujos de ML, p. ej. cuando la confianza de la predicción cae bajo un umbral.

**P:** ¿Qué son las SageMaker Model Cards?
**R:** Documentación estructurada del modelo: uso previsto, datos, métricas, limitaciones y riesgos. Herramienta de gobernanza.

**P:** ¿Qué son las AWS AI Service Cards?
**R:** Documentación de transparencia que publica AWS sobre sus propios servicios de IA: casos de uso previstos, limitaciones y buenas prácticas.

**P:** ¿Explicabilidad vs interpretabilidad?
**R:** Interpretable: el modelo se entiende por diseño (regresión, árboles). Explicable: se justifica a posteriori la salida de un modelo complejo (SHAP, importancias).

**P:** ¿Qué trade-off suele haber al exigir interpretabilidad?
**R:** Los modelos más interpretables suelen ser más simples y a veces menos precisos; con regulación de por medio, la interpretabilidad puede pesar más que el último punto de accuracy.

**P:** ¿Qué es un dataset representativo y por qué importa?
**R:** Uno que refleja la diversidad de la población real de uso. Es la palanca principal para prevenir sesgo antes de entrenar.

**P:** Medidas contra el riesgo de veracidad en gen AI de cara a clientes:
**R:** Grounding/RAG con citas, temperatura baja, guardrails, y revisión humana en decisiones de impacto.

**P:** ¿Qué es la transparencia en IA?
**R:** Comunicar qué hace el sistema, con qué datos, sus limitaciones y cuándo el usuario está interactuando con una IA.

---

## Dominio 5 — Security, Compliance, and Governance

**P:** ¿Qué es el principio de mínimo privilegio?
**R:** Conceder solo los permisos IAM imprescindibles para la tarea (p. ej. invocar un modelo concreto de Bedrock y nada más).

**P:** ¿Roles IAM vs access keys en aplicaciones?
**R:** Las aplicaciones en AWS deben asumir **roles** (credenciales temporales), no llevar access keys estáticas incrustadas.

**P:** ¿Qué hace AWS KMS?
**R:** Gestión de claves de cifrado. Con customer managed keys controlas política, rotación y auditoría del cifrado en reposo (S3, EBS, Bedrock…).

**P:** ¿Qué registra AWS CloudTrail?
**R:** Las llamadas API en la cuenta: quién, qué, cuándo y desde dónde. Es la traza de auditoría (p. ej. invocaciones de Bedrock).

**P:** ¿CloudTrail vs CloudWatch?
**R:** CloudTrail: auditoría de llamadas API (quién hizo qué). CloudWatch: métricas, logs y alarmas operativas (cómo va el sistema).

**P:** ¿Qué hace Amazon Macie?
**R:** Descubre y clasifica datos sensibles (PII) en S3 con ML. Clave antes de usar un data lake para entrenar.

**P:** ¿Macie vs GuardDuty vs Inspector?
**R:** Macie: PII en S3. GuardDuty: detección de amenazas/actividad maliciosa en la cuenta. Inspector: vulnerabilidades en workloads (EC2, ECR, Lambda).

**P:** ¿Para qué sirven los VPC endpoints (PrivateLink)?
**R:** Conectar la VPC con servicios AWS (p. ej. Bedrock) sin atravesar internet público: el tráfico queda en la red de AWS.

**P:** Modelo de responsabilidad compartida aplicado a Bedrock:
**R:** AWS asegura la infraestructura y el servicio ("de la nube"); el cliente asegura IAM, sus datos, la configuración y el uso de las salidas ("en la nube").

**P:** ¿Qué es AWS Artifact?
**R:** Portal de autoservicio para descargar informes de compliance de AWS (SOC, ISO, PCI) y aceptar acuerdos.

**P:** ¿Qué hace AWS Audit Manager?
**R:** Recopila evidencias de cumplimiento de forma continua y las mapea a frameworks (GDPR, ISO, PCI) para preparar auditorías.

**P:** ¿AWS Config vs Audit Manager?
**R:** Config evalúa continuamente la configuración de recursos contra reglas; Audit Manager recopila evidencias mapeadas a frameworks para auditorías.

**P:** ¿Qué es la residencia de datos y cómo se respeta con Bedrock?
**R:** Requisito de que los datos no salgan de una región/jurisdicción. Se usa el servicio en la región elegida; inferencia y customización se procesan allí y los datos no mejoran los modelos base.

**P:** ¿Qué es data lineage y por qué importa en gobernanza de IA?
**R:** La traza del origen y transformaciones de los datos hasta el modelo. Permite auditar calidad, permisos y cumplimiento del ciclo de vida.

**P:** ¿AgentCore Identity vs Policy in AgentCore?
**R:** Identity autentica workloads/usuarios y gestiona credenciales; Policy autoriza qué tool del Gateway puede invocar cada principal y bajo qué condiciones mediante Cedar.
