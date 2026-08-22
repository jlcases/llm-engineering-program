# Guía Dominio 2 — Fundamentals of Generative AI (~24% del examen)

> Este dominio cubre los conceptos propios de la IA generativa (tokens, embeddings, foundation models, el ciclo de vida de un FM), sus casos de uso y limitaciones, y la capa AWS vigente: **Amazon Bedrock**, SageMaker AI/JumpStart, Amazon Quick, Kiro, Strands Agents y Amazon Bedrock AgentCore.

## 1. Conceptos núcleo de generative AI

- **Generative AI**: capacidad de **generar contenido nuevo** (texto, imagen, audio, código o vídeo) a partir de patrones aprendidos. Los sistemas modernos suelen usar deep learning, pero GenAI describe la capacidad, no un escalón estricto de la jerarquía AI → ML → DL.
- **Foundation Model (FM)**: modelo grande preentrenado con datos masivos, adaptable a muchas tareas sin entrenar desde cero. Los **LLMs** son FMs de lenguaje.
- **Token**: unidad mínima que procesa un LLM (subpalabras, ~4 caracteres en inglés). El coste y los límites de contexto se miden en tokens.
- **Tokenización**: convertir texto en tokens (BPE, WordPiece).
- **Embedding**: representación **vectorial numérica** de un texto (o imagen) que captura su significado semántico; textos similares → vectores cercanos. Base de la búsqueda semántica y del RAG.
- **Vector database**: almacena embeddings y permite búsqueda por similitud. La guía 1.1 cita Amazon OpenSearch Service, Aurora, Neptune y RDS for PostgreSQL.
- **Context window**: máximo de tokens (entrada + salida) que el modelo maneja en una llamada.
- **Transformer**: arquitectura basada en **self-attention** que procesa secuencias en paralelo y captura relaciones de largo alcance; es la base de los LLMs modernos.
- Otros modelos generativos que pueden nombrar: **diffusion models** (imágenes: ruido → imagen, p. ej. Stable Diffusion), GANs, VAEs, y modelos **multimodales** (texto+imagen).

### Context engineering

**Context engineering** es diseñar todo lo que el modelo recibe en una invocación para que tenga
la información correcta en el momento correcto. Va más allá de redactar el prompt: selecciona y
ordena instrucciones, historial, memoria, documentos recuperados por RAG, resultados de tools,
ejemplos y metadatos, respetando la ventana de contexto y el presupuesto de tokens.

- Prioriza información relevante, reciente y confiable; más contexto no siempre produce más calidad.
- Separa instrucciones, datos no confiables y resultados de herramientas para reducir prompt injection.
- Resume o recupera memoria de forma selectiva en vez de reenviar conversaciones completas.
- Mide calidad, latencia y coste: cada token de entrada también consume ventana y puede facturarse.

### Fundamentos de agentic AI

- Un **agente** combina un modelo con objetivo, instrucciones, memoria y **tools** para observar, decidir y actuar.
- La **orquestación** controla la secuencia, los estados, los reintentos, las aprobaciones y los límites de ejecución.
- La **memoria** puede ser de corto plazo (estado de la sesión) o persistente (preferencias y hechos seleccionados); no equivale a reenviar todo el historial.
- **MCP (Model Context Protocol)** estandariza cómo una aplicación de IA descubre y usa herramientas, recursos y contexto de sistemas externos.
- En un patrón **multi-agent**, agentes especializados colaboran, delegan o revisan tareas. Aporta separación de responsabilidades, pero también más coste, latencia y puntos de fallo; no es mejor por defecto.

## 2. Cómo genera texto un LLM

- Predice el **siguiente token** de forma probabilística y repite (autoregresivo).
- La salida es **no determinista**: la misma entrada puede dar salidas distintas.
- **Parámetros de inferencia**:
  - **Temperature**: escala la aleatoriedad de la distribución. Baja (→0) = salidas más deterministas y repetibles; alta = más creativas/diversas.
  - **Top-p (nucleus sampling)**: limita la elección a los tokens cuya probabilidad acumulada ≤ p.
  - **Top-k**: limita la elección a los k tokens más probables.
  - **Max tokens / longitud de respuesta**: tope de tokens generados (controla coste y latencia, no calidad).
  - **Stop sequences**: cadenas que detienen la generación.

## 3. Ciclo de vida de un foundation model

1. **Data selection**: corpus masivo (a menudo self-supervised, sin etiquetas manuales).
2. **Pre-training**: aprender lenguaje general prediciendo tokens; carísimo (GPUs, semanas).
3. **Continued pre-training**: seguir el pre-training con datos **de dominio sin etiquetar** (jerga médica, legal...).
4. **Fine-tuning**: ajustar pesos con datos **etiquetados** de la tarea (instruction tuning con pares prompt-respuesta).
5. **RLHF (Reinforcement Learning from Human Feedback)**: alinear el modelo con preferencias humanas usando un reward model.
6. **Evaluación**: benchmarks y métricas (ver §6).
7. **Despliegue e iteración**.

## 4. Casos de uso, ventajas y limitaciones

- **Casos de uso**: chatbots y asistentes, resumen, generación y explicación de código, extracción y clasificación, traducción, búsqueda semántica, generación de imágenes, agentes.
- **Ventajas**: adaptabilidad a muchas tareas, poco o ningún dato de entrenamiento propio (zero/few-shot), time-to-market rápido.
- **Limitaciones que el examen explota**:
  - **Hallucinations**: respuestas fluidas pero falsas, dichas con confianza. Mitigación: RAG/grounding, revisión humana, temperature baja, Guardrails con contextual grounding check.
  - **Knowledge cutoff**: el modelo no conoce hechos posteriores a su entrenamiento → RAG para datos actuales.
  - **No determinismo**, sesgos heredados de los datos, riesgo de exposición de datos (prompt injection, fuga de PII), coste de inferencia, **falta de interpretabilidad** (los FMs son menos explicables que un árbol de decisión).

## 5. Cómo adaptar un FM (de más barato a más caro)

1. **Prompt engineering**: instrucciones y ejemplos en el prompt; sin tocar pesos.
2. **RAG (Retrieval-Augmented Generation)**: recuperar documentos relevantes de una fuente externa (vector DB) e inyectarlos en el prompt. Da acceso a datos **propios y actualizados sin reentrenar**; reduce hallucinations; el conocimiento se actualiza actualizando la base, no el modelo.
3. **Fine-tuning**: reentrenar parcialmente los pesos con datos etiquetados; cambia el **comportamiento/estilo/tarea**. Variantes eficientes: **PEFT/LoRA** (entrenar pocos parámetros adicionales).
4. **Entrenar desde cero**: casi nunca es la respuesta correcta (coste extremo).

Regla de examen: "conocimiento actualizado o propietario" → **RAG**; "tono, formato o tarea especializada de forma consistente" → **fine-tuning**; "mínimo coste/esfuerzo" → **prompt engineering**.

## 6. Evaluación de modelos generativos

- **ROUGE**: solapamiento con referencia; típico para **resumen**.
- **BLEU**: precisión de n-gramas; típico para **traducción**.
- **BERTScore**: similitud semántica con embeddings (no solo palabras exactas).
- **Perplexity**: cuán "sorprendido" está el modelo por el texto; menor = mejor modelado del lenguaje.
- **Human evaluation / LLM-as-a-judge**: para calidad general.
- Benchmarks: MMLU, HELM, etc. (basta saber que existen y para qué sirven).
- En AWS: **Amazon Bedrock model evaluation** (automática o con human review) y **SageMaker Clarify** para evaluación de FMs.

## 7. Generative AI en AWS

- **Amazon Bedrock**: servicio **serverless y totalmente gestionado** para invocar FMs de varios proveedores (Amazon Titan/Nova, Anthropic Claude, Meta Llama, Mistral, Cohere, Stability AI...) vía una **API única**. Sin infraestructura que gestionar. Piezas clave:
  - **Model choice**: comparar y cambiar de modelo sin cambiar de plataforma; playgrounds para experimentar.
  - **Knowledge Bases**: **RAG gestionado** — ingesta desde S3 y otras fuentes, chunking, embeddings y vector store gestionados.
  - **Agents**: orquestan tareas multi-paso llamando APIs/Lambda (action groups) y Knowledge Bases.
  - **Guardrails**: filtros de contenido, denied topics, PII redaction, contextual grounding (Dominio 4).
  - **Custom models**: fine-tuning y continued pre-training sobre ciertos modelos; los datos del cliente **no** se usan para entrenar los modelos base.
  - **Provisioned throughput** vs **on-demand** (ver §8 precios).
- **Amazon SageMaker JumpStart**: hub de FMs y modelos preentrenados para **desplegar en tu propia infraestructura SageMaker** con más control (instancias, redes) y fine-tuning; más flexibilidad, más gestión.
- **Amazon Q Developer**: asistente de código (autocompletado, chat, seguridad) — sucesor de CodeWhisperer.
- **Amazon Q Business**: asistente generativo empresarial conectado a datos corporativos con permisos.
- **Amazon Quick**: workspace gestionado con chat, agentes, análisis/visualización, investigación y automatización sobre datos conectados. Amazon Quick Sight es su capacidad de BI.
- **Kiro**: IDE agéntico orientado a desarrollo guiado por especificaciones, steering files y hooks de calidad.
- **Strands Agents**: SDK open source y model-first para construir agentes con tools, varios proveedores y protocolos como MCP.
- **Amazon Bedrock AgentCore**: infraestructura model- y framework-agnostic para desplegar y operar agentes. Incluye Runtime, Gateway, Memory, Identity, Observability, Evaluations y Policy.
- **AWS Transform**: servicio agéntico para modernizar aplicaciones y workloads; está en la lista de servicios en alcance de la revisión 1.1.
- **Amazon Titan / Nova**: familias de FMs propios de Amazon (texto, embeddings, imagen).
- Infraestructura: **AWS Trainium** (chip para entrenar), **AWS Inferentia** (chip para inferencia), GPUs NVIDIA en EC2.

## 8. Precios y throughput en Bedrock

- **Token-based pricing**: la inferencia se cobra normalmente por tokens de entrada y de salida. Un contexto más largo puede aumentar coste y latencia antes incluso de generar la respuesta.
- **On-demand**: pago por token (input + output); sin compromiso; para cargas variables o experimentación.
- **Provisioned throughput**: capacidad reservada (model units) con compromiso temporal; para cargas de producción sostenidas y predecibles; **obligatorio para modelos custom/fine-tuneados**.
- **Batch inference**: procesar lotes con descuento cuando no hay urgencia.
- Palancas de coste: modelo más pequeño, menos tokens (prompts concisos, límites de salida), caching, batch.

## 9. Trampas típicas del examen

- **Bedrock vs SageMaker JumpStart**: API serverless sin gestionar infraestructura → **Bedrock**; control de infraestructura/instancias y personalización profunda → **JumpStart**.
- **RAG vs fine-tuning**: "documentos internos que cambian a diario" → RAG (Knowledge Bases), no fine-tuning.
- **Continued pre-training vs fine-tuning**: datos de dominio **sin etiquetar** → continued pre-training; pares etiquetados prompt-respuesta → fine-tuning.
- **Temperature vs top-p vs max tokens**: "respuestas más consistentes/repetibles" → bajar temperature; "limitar longitud y coste" → max tokens.
- **Embeddings**: si la pregunta habla de "búsqueda semántica" o "similitud de significado" → modelo de embeddings + vector DB, no un LLM de chat.
- **Hallucinations**: la mitigación correcta suele ser **RAG/grounding + human oversight**, no "más temperature" ni "más tokens".
- **Amazon Q Developer vs Q Business**: código para desarrolladores vs asistente sobre datos de la empresa.
- **Prompt engineering vs context engineering**: el primero diseña instrucciones y ejemplos; el segundo diseña además memoria, retrieval, tools, historial y presupuesto de contexto.
- **Agente único vs multi-agent**: usa varios agentes solo cuando la especialización o revisión compensa la coordinación, el coste y la latencia añadidos.
- **Strands vs AgentCore**: Strands es un SDK para construir la lógica; AgentCore aporta infraestructura gestionada para ejecutar, conectar, recordar, autorizar y observar agentes hechos con Strands, LangGraph, CrewAI o código propio.
- **Bedrock Agents vs AgentCore**: Bedrock Agents ofrece orquestación gestionada con action groups y knowledge bases; AgentCore hospeda y opera código de agentes de cualquier framework.
- **Knowledge cutoff**: "el chatbot no sabe de los productos lanzados el mes pasado" → RAG, no reentrenar desde cero.
- **Provisioned throughput**: aparece como respuesta correcta cuando el escenario pide **rendimiento garantizado** para producción o **usar un modelo fine-tuneado** en Bedrock.

## 10. Mini-escenarios de repaso (formato examen)

- *"Queremos probar varios FMs de distintos proveedores con una sola API y sin gestionar servidores."* → Amazon Bedrock.
- *"Necesitamos desplegar un modelo open-source con control total de las instancias y la red."* → SageMaker JumpStart.
- *"El chatbot inventa respuestas sobre políticas internas."* → RAG con Bedrock Knowledge Bases (grounding), no fine-tuning.
- *"Queremos que el modelo escriba siempre con el tono legal de la firma."* → Fine-tuning (datos etiquetados de ejemplo).
- *"Tenemos 50 GB de informes médicos sin etiquetar y el modelo no entiende la jerga."* → Continued pre-training.
- *"Las respuestas del asistente de soporte deben ser consistentes y repetibles."* → Bajar temperature (≈0).
- *"Hay que acortar las respuestas para reducir coste."* → Limitar max tokens.
- *"El agente recibe historial, memoria, documentos y tools, pero supera la ventana y pierde instrucciones."* → Aplicar context engineering: seleccionar, ordenar y presupuestar el contexto.
- *"Varios agentes deben descubrir herramientas externas con una interfaz común."* → MCP para la conexión; orquestación para coordinar el workflow.
- *"¿Qué métrica para evaluar el resumidor de noticias?"* → ROUGE.
- *"¿Qué métrica para evaluar el traductor?"* → BLEU.
- *"Buscar productos 'parecidos' semánticamente a la consulta del usuario."* → Embeddings (Titan Embeddings) + vector database.
- *"Los desarrolladores quieren autocompletado de código con IA."* → Amazon Q Developer.
- *"Empleados preguntando sobre documentación interna con permisos corporativos."* → Amazon Q Business.
- *"Analizar datos, investigar y automatizar trabajo empresarial mediante chat y agentes sin construir una plataforma propia."* → Amazon Quick.
- *"Construir en Python un agente model-first, open source y conectado a tools."* → Strands Agents.
- *"Hospedar un agente de LangGraph con runtime aislado, memoria, identidad, gateway y observabilidad gestionados."* → Amazon Bedrock AgentCore.
- *"Desarrollo agéntico guiado por especificaciones, steering y hooks de calidad."* → Kiro.
- *"Producción con tráfico alto y sostenido, y un modelo fine-tuneado en Bedrock."* → Provisioned throughput.

## 11. Glosario rápido

| Término | Definición de examen |
|---|---|
| Foundation model | Modelo grande preentrenado adaptable a muchas tareas |
| LLM | FM especializado en lenguaje natural |
| Token | Unidad de texto que procesa el modelo (~subpalabra) |
| Embedding | Vector numérico que representa significado |
| Context window | Máximo de tokens por invocación (entrada+salida) |
| Temperature | Control de aleatoriedad de la generación |
| Top-p / top-k | Restricción del muestreo de tokens candidatos |
| Prompt | Entrada con instrucciones/contexto para el modelo |
| Inference | Generación de la respuesta del modelo |
| Pre-training | Entrenamiento inicial masivo self-supervised |
| Fine-tuning | Ajuste de pesos con datos etiquetados de la tarea |
| RLHF | Alineación con preferencias humanas vía reward model |
| RAG | Recuperar contexto externo e inyectarlo en el prompt |
| Hallucination | Salida plausible pero factualmente falsa |
| Multimodal | Modelo que combina modalidades (texto+imagen...) |
| Diffusion model | Generador de imágenes por eliminación de ruido |
| Agent | LLM que planifica y ejecuta acciones con herramientas |
| Context engineering | Selección y composición de instrucciones, memoria, retrieval, tools e historial dentro del presupuesto de contexto |
| MCP | Protocolo para conectar aplicaciones de IA con tools, recursos y contexto externos |

## 12. Checklist antes del examen

- [ ] Sé qué es un token, un embedding y un context window, y qué se cobra por token.
- [ ] Distingo prompt engineering de context engineering y sé presupuestar memoria, RAG, tools e historial.
- [ ] Explico agente, tool, memoria, orquestación, MCP y cuándo compensa un patrón multi-agent.
- [ ] Explico temperature, top-p, top-k, max tokens y stop sequences y qué ajusta cada uno.
- [ ] Ordeno la escalera prompt engineering → RAG → fine-tuning → continued pre-training → from scratch por coste.
- [ ] Distingo fine-tuning (etiquetado) de continued pre-training (sin etiquetar).
- [ ] Asocio ROUGE↔resumen, BLEU↔traducción, BERTScore↔similitud semántica, perplexity↔modelado.
- [ ] Distingo Bedrock (serverless, API) de SageMaker JumpStart (tu infra, más control).
- [ ] Enumero las piezas de Bedrock: Knowledge Bases, Agents, Guardrails, model evaluation, custom models.
- [ ] Sé cuándo elegir on-demand, provisioned throughput y batch inference.
- [ ] Distingo Amazon Q Developer, Q Business y Amazon Quick.
- [ ] Distingo el SDK Strands Agents, Bedrock Agents y la infraestructura Amazon Bedrock AgentCore.
- [ ] Sé para qué se usan Kiro y AWS Transform en el alcance actual.
- [ ] Sé que Trainium entrena e Inferentia sirve inferencia.

## Mapeo al repo

Este dominio se corresponde con los **módulos 1 (fundamentos y Bedrock) y 2 (prompting básico)**, con apoyo del módulo 3 para embeddings/RAG.

---

> ⚠️ **Nota**: los contenidos, pesos y servicios citados pueden cambiar. Cobertura contrastada con
> los [objetivos oficiales del Dominio 2](https://docs.aws.amazon.com/aws-certification/latest/ai-practitioner-01/ai-practitioner-01-domain2.html)
> el **21 de agosto de 2026**.
