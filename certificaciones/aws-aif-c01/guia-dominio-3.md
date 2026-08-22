# Guía Dominio 3 — Applications of Foundation Models (~28% del examen)

> El dominio con **más peso** del examen. Cubre cómo se aplican los FMs en la práctica: criterios de selección de modelo, prompt engineering en profundidad, RAG y vector stores, fine-tuning, agentes, y cómo evaluar la aplicación resultante. Muchas preguntas son escenarios de "¿qué enfoque/servicio elijo?".

## 1. Criterios para elegir un foundation model

Factores que el examen espera que ponderes:

- **Coste** (por token, por hora de instancia, provisioned vs on-demand).
- **Latencia**: modelos más pequeños responden más rápido; importa en chatbots en tiempo real.
- **Modalidad**: texto, imagen, embeddings, multimodal.
- **Context window**: documentos largos → ventana grande.
- **Idiomas soportados**, calidad en el dominio, tamaño del modelo (capacidad vs coste/latencia).
- **Personalización disponible**: ¿permite fine-tuning? ¿continued pre-training?
- **Licencia y proveedor** (modelos abiertos vs propietarios).
- Tradeoff clásico: **modelo grande = más capacidad, más coste y latencia**; modelo pequeño = más barato/rápido, menos capaz. No existe "el mejor modelo": depende del caso de uso.

## 2. Prompt engineering (a fondo)

- **Partes de un prompt**: instrucción, contexto, input data, output indicator (formato deseado).
- **Zero-shot**: solo la instrucción, sin ejemplos.
- **Few-shot**: incluir ejemplos entrada→salida en el prompt para guiar formato y estilo (one-shot = 1 ejemplo).
- **Chain-of-thought (CoT)**: pedir razonamiento paso a paso ("think step by step"); mejora tareas de lógica/matemáticas.
- **Prompt templates**: plantillas reutilizables con variables.
- **Negative prompting**: indicar explícitamente qué NO debe hacer/incluir.
- **System prompt / rol**: fija el comportamiento global del asistente.
- Buenas prácticas: instrucciones claras y específicas, delimitadores para separar contexto, especificar formato de salida, iterar y evaluar.

### Versionado y Amazon Bedrock Prompt Management

- Trata el prompt como un artefacto versionado: identificador estable, versión inmutable, variables declaradas, configuración del modelo, autor, fecha y notas de cambio.
- **Amazon Bedrock Prompt Management** permite crear, guardar, probar y versionar prompts y sus variantes para reutilizarlos en aplicaciones y workflows.
- Compara versiones con el mismo dataset y métricas antes de promoverlas; conserva una versión anterior para rollback.
- Separa la versión del prompt de la versión del modelo y del dataset de evaluación. Cambiar cualquiera puede alterar el resultado.

### Riesgos de prompting (prompt attacks)
- **Prompt injection**: instrucciones maliciosas inyectadas en el input (o en documentos recuperados — indirect injection) para secuestrar el comportamiento.
- **Jailbreaking**: técnicas para saltarse las políticas de seguridad del modelo.
- **Prompt leaking**: conseguir que el modelo revele su system prompt o datos internos.
- Mitigaciones: Bedrock **Guardrails**, validación/sanitización de inputs, separar instrucciones de datos, mínimos privilegios en las herramientas del modelo.

## 3. RAG y vector databases

- **RAG**: (1) query del usuario → (2) buscar fragmentos relevantes por similitud de embeddings en un vector store → (3) inyectarlos en el prompt → (4) el LLM responde **grounded** en esos datos.
- Beneficios: conocimiento actualizado y propietario, menos hallucinations, citación de fuentes, sin coste de reentrenar.
- **Chunking**: partir documentos en fragmentos para indexar; el tamaño de chunk afecta la calidad del retrieval.
- **Amazon Bedrock Knowledge Bases**: RAG totalmente gestionado — conecta S3/Confluence/Salesforce/SharePoint/web, gestiona chunking, embeddings (p. ej. Titan Embeddings) y el vector store, y responde con citas.
- **Vector stores citados en el objetivo 3.1**: Amazon **OpenSearch Service**, **Aurora**, **Neptune** y **RDS for PostgreSQL**. OpenSearch y PostgreSQL con pgvector son los distractores más frecuentes en escenarios de RAG.

## 4. Personalización: cuándo cada técnica

Escalera de menor a mayor coste/complejidad:

1. **Prompt engineering** — sin datos, sin entrenar. Primero siempre.
2. **RAG** — conocimiento externo actualizable; no cambia el modelo.
3. **Fine-tuning** — cambia pesos con datos **etiquetados**; para estilo, formato, tarea específica. **PEFT/LoRA** reduce el coste entrenando pocos parámetros.
4. **Continued pre-training** — datos de dominio **sin etiquetar** para vocabulario/jerga.
5. **Entrenar desde cero** — prácticamente nunca.

Preparación de datos para fine-tuning: calidad sobre cantidad, datos representativos y limpios, formato de pares prompt-completion, curación y gobernanza (data curation). En Bedrock, el fine-tuning crea un **custom model** que requiere **provisioned throughput** para servirse.

## 5. Agentes (agents for generative AI)

- Un **agente** usa un LLM para **planificar y ejecutar tareas multi-paso**, decidiendo qué **herramientas/APIs** llamar (razonamiento tipo ReAct: pensar → actuar → observar).
- **Amazon Bedrock Agents**: agentes gestionados — **action groups** (APIs/Lambda que el agente puede invocar, definidas con esquemas OpenAPI), integración con **Knowledge Bases**, memoria de sesión, y trazas de razonamiento.
- Caso de examen: "el chatbot debe consultar el estado del pedido en una API y además responder con la política de devoluciones" → Bedrock Agent con action group + Knowledge Base.

## 6. Evaluación de aplicaciones con FMs

- Métricas automáticas: **ROUGE** (resumen), **BLEU** (traducción), **BERTScore** (similitud semántica), exact match/F1 (QA).
- **Human evaluation**: calidad subjetiva, tono, utilidad.
- **LLM-as-a-judge**: un modelo evalúa las salidas de otro (escalable, más barato que humanos).
- **Bedrock model evaluation**: jobs de evaluación automáticos (accuracy, robustness, toxicity) o con workforce humana.
- Evaluar también el **negocio**: satisfacción de usuario, tasa de resolución, coste por consulta, latencia.
- Para RAG: calidad del retrieval (¿recuperó lo relevante?) y de la generación (faithfulness al contexto).
- Para agentes y workflows: tasa de finalización, selección correcta de tools, éxito por paso, recuperación ante errores, intervenciones humanas, coste y latencia end-to-end.
- Evalúa el **sistema completo**, no solo el FM: una buena respuesta final puede ocultar pasos inseguros o llamadas innecesarias.

## 7. Arquitecturas y servicios de apoyo

- **Amazon S3**: almacén de documentos fuente para Knowledge Bases y datos de entrenamiento.
- **AWS Lambda**: lógica de action groups y glue code serverless.
- **API Gateway**: exponer la app generativa como API.
- **Step Functions**: orquestación de workflows.
- **CloudWatch**: métricas y logs de la aplicación (invocaciones, latencia).
- **Playgrounds de Bedrock**: experimentación manual antes de convertir el prompt y la configuración en código evaluable.

## 8. Trampas típicas del examen

- **"Datos que cambian constantemente" → RAG**, no fine-tuning. **"Adoptar un tono/estilo de marca consistente" → fine-tuning**, no RAG.
- **Few-shot vs fine-tuning**: si bastan unos ejemplos en el prompt, few-shot es más barato y suele ser la respuesta con "least effort".
- **CoT**: la respuesta a "el modelo falla en problemas de razonamiento de varios pasos" es chain-of-thought, no subir temperature.
- **Knowledge Bases vs Agents**: solo responder con documentos → Knowledge Base; **ejecutar acciones**/llamar APIs → Agents (con action groups).
- **Chunking**: aparece como parte del pipeline RAG (preguntas de "¿qué paso falta entre ingesta y embedding?").
- **Embeddings model vs text model**: para indexar documentos se usa un **embedding model** (Titan Embeddings), no el LLM generador.
- **ROUGE vs BLEU**: resumen → ROUGE; traducción → BLEU. Lo preguntan directamente.
- **Model size tradeoff**: "reducir latencia y coste aceptando algo menos de calidad" → modelo más pequeño; nunca "más provisioned throughput" si el problema es el tamaño del modelo.
- **Temperatura para tareas factuales**: apps de soporte/factuales → temperature baja; creatividad (marketing) → alta.
- **Prompt injection**: la mitigación en AWS es **Bedrock Guardrails** + validación de inputs; "reentrenar el modelo" es distractor.
- **Custom model en Bedrock** → requiere **provisioned throughput** (no se sirve on-demand).
- **Prompt nuevo en producción**: versionarlo en Bedrock Prompt Management, evaluarlo con un dataset estable y mantener rollback; copiar texto a mano entre entornos no es una estrategia.

## 9. Mini-escenarios de repaso (formato examen)

- *"El asistente debe responder sobre el catálogo, que cambia cada semana."* → RAG con Bedrock Knowledge Bases.
- *"El modelo debe clasificar tickets siguiendo exactamente nuestro formato de 5 categorías; tenemos 20 ejemplos."* → Few-shot prompting (antes que fine-tuning).
- *"El modelo falla en cálculos de varios pasos."* → Chain-of-thought prompting.
- *"El chatbot debe consultar el estado del pedido en nuestra API y cancelarlo si el cliente lo pide."* → Bedrock Agent con action groups.
- *"Además, debe responder dudas sobre la política de devoluciones (PDFs en S3)."* → Asociar una Knowledge Base al agente.
- *"¿Qué paso convierte los documentos en fragmentos indexables?"* → Chunking, luego embeddings al vector store.
- *"Usuarios malintencionados hacen que el bot ignore sus instrucciones."* → Prompt injection → Bedrock Guardrails + validación de input.
- *"Elegir modelo para un chatbot de alta concurrencia sensible a latencia y coste."* → Modelo más pequeño/rápido, aunque pierda algo de calidad.
- *"Medir si el resumidor cubre el contenido de referencia."* → ROUGE.
- *"Evaluar miles de respuestas sin coste de anotadores humanos."* → LLM-as-a-judge (o Bedrock model evaluation automática).
- *"Comparar una nueva plantilla con la versión de producción y poder volver atrás."* → Bedrock Prompt Management + evaluación versionada.
- *"El agente responde bien, pero ejecuta tools innecesarias y falla pasos intermedios."* → Evaluar la aplicación/agente por paso y end-to-end, no solo el texto final.
- *"Servir el modelo fine-tuneado en Bedrock en producción."* → Provisioned throughput.
- *"¿Dónde guardo los embeddings en AWS?"* → OpenSearch Service/Serverless (o pgvector en Aurora/RDS).

## 10. Glosario rápido

| Término | Definición de examen |
|---|---|
| Zero-shot | Prompt sin ejemplos |
| Few-shot | Prompt con ejemplos entrada→salida |
| Chain-of-thought | Pedir razonamiento paso a paso |
| Prompt template | Plantilla de prompt con variables reutilizables |
| Prompt Management | Servicio de Bedrock para guardar, probar, versionar y reutilizar prompts |
| Negative prompt | Indicar qué NO debe hacer/incluir |
| Prompt injection | Input malicioso que secuestra las instrucciones |
| Jailbreaking | Saltarse las políticas de seguridad del modelo |
| Prompt leaking | Extraer el system prompt o datos internos |
| Chunking | Partir documentos en fragmentos indexables |
| Vector store | Base de datos de embeddings con búsqueda por similitud |
| Grounding | Anclar la respuesta a fuentes recuperadas |
| Action group | Conjunto de APIs/Lambda que un Bedrock Agent puede invocar |
| ReAct | Patrón razonar→actuar→observar de los agentes |
| PEFT / LoRA | Fine-tuning eficiente entrenando pocos parámetros |
| Instruction tuning | Fine-tuning con pares instrucción→respuesta |
| LLM-as-a-judge | Un LLM evalúa las salidas de otro |
| Latencia vs throughput | Tiempo por respuesta vs volumen procesado por unidad de tiempo |

## 11. Checklist antes del examen

- [ ] Enumero los criterios de selección de FM: coste, latencia, modalidad, context window, personalización, licencia.
- [ ] Distingo zero-shot, few-shot y chain-of-thought y cuándo aplicar cada uno.
- [ ] Versiono prompts con Bedrock Prompt Management, dataset de evaluación y rollback.
- [ ] Explico el pipeline RAG completo: ingesta → chunking → embeddings → vector store → retrieval → generación.
- [ ] Sé qué gestiona Bedrock Knowledge Bases y qué fuentes acepta.
- [ ] Distingo Knowledge Base (responder con documentos) de Agent (ejecutar acciones).
- [ ] Sé qué es un action group y que se define con esquemas de API.
- [ ] Ubico ROUGE, BLEU, BERTScore y LLM-as-a-judge en la tarea correcta.
- [ ] Evalúo RAG, agentes y workflows por componentes y también end-to-end.
- [ ] Identifico prompt injection/jailbreak/leaking y sus mitigaciones.
- [ ] Recuerdo que custom models en Bedrock exigen provisioned throughput.
- [ ] Ante "least effort/cost", pruebo mentalmente prompt engineering → RAG → fine-tuning en ese orden.

## 12. Cómo leer las preguntas de este dominio

Las preguntas de escenario del Dominio 3 casi siempre esconden la respuesta en una restricción:

1. Subraya mentalmente la restricción operativa: "least effort", "lowest cost", "data changes daily", "must call an API", "no internet access", "consistent brand voice".
2. Mapea la restricción a la técnica: effort/cost → prompt engineering; datos cambiantes → RAG; acciones → Agents; estilo consistente → fine-tuning.
3. Descarta los distractores que resuelven **otro** problema (reentrenar cuando el problema es conocimiento fresco; subir throughput cuando el problema es tamaño de modelo).
4. Entre dos opciones válidas, gana la **gestionada** y la **más barata** que cumpla todos los requisitos.

## Mapeo al repo

Este dominio es el corazón práctico del programa: **módulo 2 (prompt engineering), módulo 3 (RAG y evaluación) y módulo 4 (agentes, Bedrock Agents, MCP)**.

---

> ⚠️ **Nota**: los contenidos, pesos y servicios citados pueden cambiar. Cobertura contrastada con
> los [objetivos oficiales del Dominio 3](https://docs.aws.amazon.com/aws-certification/latest/ai-practitioner-01/ai-practitioner-01-domain3.html)
> el **21 de agosto de 2026**.
