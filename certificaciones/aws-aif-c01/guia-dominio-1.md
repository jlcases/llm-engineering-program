# Guía Dominio 1 — Fundamentals of AI and ML (20% del examen)

> Este dominio pregunta por conceptos básicos de AI/ML, tipos de aprendizaje, casos de uso,
> inferencia y ciclo de vida. La revisión 1.1 añade de forma explícita **agentic AI**, la elección
> entre ML tradicional y foundation models, y servicios actuales como Amazon Bedrock, Amazon Q,
> Amazon Quick y Kiro.

## 1. Conceptos base: AI, ML, deep learning, GenAI y agentic AI

- **Artificial Intelligence (AI)**: campo amplio; cualquier técnica que permite a una máquina imitar comportamiento inteligente humano (incluye sistemas de reglas, no solo aprendizaje).
- **Machine Learning (ML)**: subconjunto de AI; el sistema aprende patrones a partir de datos en lugar de reglas programadas explícitamente.
- **Deep Learning (DL)**: subconjunto de ML basado en redes neuronales con múltiples capas; destaca en datos no estructurados (imagen, audio, texto).
- **Generative AI (GenAI)**: crea contenido nuevo —texto, imagen, audio, vídeo o código— a partir de los patrones aprendidos. Los LLM y otros foundation models modernos suelen usar deep learning.
- **Agentic AI**: sistemas que persiguen un objetivo mediante planificación, memoria, herramientas y uno o varios agentes. No es un nivel adicional de la jerarquía: es un patrón de aplicación que normalmente usa modelos generativos.
- Relación segura para el examen: **ML es parte de AI y DL es parte de ML**. GenAI describe qué produce el sistema; agentic AI, cómo organiza acciones para lograr un objetivo. Evita tratarlos como subconjuntos estrictos intercambiables.
- **Datos estructurados** (tablas, CSV) vs **no estructurados** (texto, imágenes, audio) vs **semiestructurados** (JSON, XML). DL brilla en no estructurados; ML clásico suele bastar para tabulares.

## 2. Tipos de aprendizaje

| Tipo | Datos | Ejemplos de uso |
|---|---|---|
| **Supervised learning** | Etiquetados (features + label) | Clasificación de spam, predicción de precio (regresión) |
| **Unsupervised learning** | Sin etiquetas | Clustering de clientes, detección de anomalías, reducción de dimensionalidad |
| **Semi-supervised** | Pocos etiquetados + muchos sin etiquetar | Clasificación con etiquetado caro |
| **Reinforcement learning (RL)** | Agente + entorno + recompensas | Robótica, control y juegos |
| **Self-supervised** | Las etiquetas salen de los propios datos | Pre-training de LLMs (predecir el siguiente token) |

- **Clasificación** (label discreta: binaria o multiclase) vs **regresión** (valor continuo). Si la pregunta dice "predecir el precio / la demanda / un número" → regresión; "clasificar en categorías / detectar fraude sí-no" → clasificación.
- **Clustering** no tiene etiquetas: si el escenario dice "agrupar clientes similares sin categorías predefinidas" → unsupervised (K-means).

## 3. Ciclo de vida de ML (ML lifecycle)

1. **Definición del problema de negocio** (¿hace falta ML siquiera? Si las reglas fijas bastan, no uses ML).
2. **Recolección y preparación de datos**: limpieza, manejo de valores faltantes, **feature engineering**, split train/validation/test.
3. **Entrenamiento**: selección de algoritmo, ajuste de **hyperparameters** (los fija el humano antes de entrenar) vs **parameters/weights** (los aprende el modelo).
4. **Evaluación**: métricas sobre datos de test que el modelo no ha visto.
5. **Despliegue**: real-time endpoint vs batch inference.
6. **Monitorización**: detección de **data drift** y **model drift**; reentrenamiento.
- **MLOps**: aplicar prácticas DevOps al ciclo ML (automatización, CI/CD de modelos, versionado de datos y modelos, monitorización continua).

### Fuentes y formas de servir modelos

- **Modelo preentrenado open source**: acelera el inicio y permite inspección o alojamiento propio, pero el equipo asume evaluación, seguridad, capacidad y operación.
- **Modelo propio**: máximo control y especialización; exige datos, cómputo, talento y mantenimiento.
- **API gestionada**: menor carga operativa y escalado delegado al proveedor.
- **API self-hosted**: más control sobre infraestructura, residencia y optimización, a cambio de operar el servicio.

## 4. Overfitting, underfitting y calidad del modelo

- **Overfitting**: excelente en training, malo en test → memoriza en vez de generalizar. Mitigación: más datos, regularización, early stopping, dropout, modelos más simples.
- **Underfitting**: malo en training y en test → modelo demasiado simple o datos/features insuficientes.
- **Bias-variance tradeoff**: alto bias ≈ underfitting; alta variance ≈ overfitting.

## 5. Métricas técnicas y de negocio

- **Clasificación**: confusion matrix, **accuracy** (engañosa con clases desbalanceadas), **precision** (de lo que predije positivo, cuánto acerté — importa cuando el falso positivo es caro), **recall** (de los positivos reales, cuántos detecté — importa cuando el falso negativo es caro, p. ej. detección de cáncer o fraude), **F1** (media armónica de ambas), **AUC-ROC**.
- **Regresión**: MAE, MSE, **RMSE**, R².
- **Negocio**: coste por usuario o interacción, coste de desarrollo, satisfacción y feedback de clientes, tasa de finalización y **ROI**. Un modelo técnicamente mejor no aporta valor si empeora el coste, la latencia o el resultado de negocio.
- Truco de examen: "detectar la mayor cantidad posible de casos de fraude aunque haya falsas alarmas" → maximizar **recall**; "evitar acusar a clientes inocentes" → **precision**.

## 6. Inferencia: modalidades

- **Real-time inference**: baja latencia, endpoint siempre activo, tráfico sostenido.
- **Batch (transform)**: grandes volúmenes sin urgencia; más barato, sin endpoint persistente.
- **Asynchronous inference**: payloads grandes, latencia tolerante, cola de peticiones.
- **Serverless inference**: tráfico intermitente o impredecible, pagar por uso, tolera cold starts.

## 7. Elegir ML tradicional, un foundation model o reglas

| Enfoque | Cuándo encaja mejor |
|---|---|
| Reglas deterministas | Resultado exacto, política estable y lógica explicable; no hace falta predecir |
| ML tradicional | Datos tabulares o series temporales, objetivo acotado, menor coste/latencia y alta explicabilidad |
| Foundation model | Texto, imagen o tareas abiertas; generación, resumen, conversación y adaptación entre dominios |
| Sistema agéntico | Objetivo multietapa que necesita herramientas, memoria, decisiones y orquestación |

En sectores regulados, la explicabilidad, la privacidad, el coste y las restricciones operativas
pueden hacer preferible un modelo tradicional aunque un FM sea capaz de resolver la tarea.

## 8. Servicios AWS de AI/ML: cuál elegir

Regla general del examen: **si existe un servicio de AI gestionado que resuelve el caso de uso, es la respuesta** (menor esfuerzo operativo); SageMaker AI es para cuando necesitas construir o entrenar modelos propios.

### Servicios de AI preentrenados (no requieren expertise ML)
- **Amazon Comprehend**: NLP sobre texto — sentimiento, entidades, key phrases, PII detection, clasificación de documentos.
- **Amazon Rekognition**: visión — objetos, caras, moderación de contenido en imágenes y vídeo, texto en imágenes.
- **Amazon Textract**: **extraer texto, tablas y formularios de documentos escaneados/PDF** (más que OCR simple: entiende estructura).
- **Amazon Transcribe**: speech-to-text (audio → texto).
- **Amazon Polly**: text-to-speech (texto → voz).
- **Amazon Translate**: traducción automática entre idiomas.
- **Amazon Lex**: chatbots conversacionales con voz y texto (el motor de Alexa).
- **Amazon Kendra**: **búsqueda empresarial inteligente** con lenguaje natural sobre repositorios de documentos.
- **Amazon Personalize**: recomendaciones personalizadas (estilo Amazon.com) sin expertise ML.
- **Amazon Q Business**: asistente empresarial generativo sobre los datos de la empresa.

### Plataforma, foundation models y trabajo agéntico

- **Amazon Bedrock**: acceso gestionado mediante API a foundation models y capacidades para crear aplicaciones de GenAI y agentes sin administrar la infraestructura del modelo.
- **Amazon SageMaker AI**: plataforma para crear, entrenar, adaptar, desplegar y monitorizar modelos con mayor control sobre el ciclo ML.
- **SageMaker JumpStart**: catálogo y punto de partida para modelos y soluciones preentrenadas dentro de SageMaker AI.
- **Amazon Q**: familia de asistentes para trabajo empresarial y desarrollo de software.
- **Amazon Quick**: workspace de IA para investigar, analizar datos, visualizar y automatizar trabajo con chat y agentes.
- **Kiro**: entorno de desarrollo agéntico guiado por especificaciones, steering y hooks.
- **Strands Agents**: SDK open source para construir agentes; **Amazon Bedrock AgentCore** aporta infraestructura gestionada para ejecutarlos y operarlos.
- **Amazon Nova**: familia de foundation models de AWS disponible en el ecosistema de Bedrock.
- **AWS Transform**: servicio agéntico para modernizar aplicaciones y cargas de trabajo.

### Humano en el bucle
- **Amazon A2I (Augmented AI)**: incorpora **revisión humana** de predicciones de baja confianza (p. ej. revisar extracciones de Textract dudosas).

## 9. Trampas típicas del examen

- **AI vs ML vs DL**: si el sistema usa reglas fijas escritas a mano, es AI pero **no** ML.
- **"Sin experiencia en ML" / "least operational overhead"** → servicio de AI gestionado (Comprehend, Rekognition...), **no** SageMaker AI.
- **Textract vs Rekognition**: documentos/formularios → Textract; fotos/vídeo/caras → Rekognition (aunque Rekognition también lee texto en imágenes de escenas, p. ej. matrículas).
- **Kendra vs Personalize**: búsqueda de documentos → Kendra; recomendaciones de productos/contenido → Personalize.
- **Transcribe vs Polly**: son inversos — audio→texto vs texto→audio. Leer con calma el sentido de la conversión.
- **Hyperparameter vs parameter**: hyperparameter lo fija el humano antes del training (learning rate, epochs); parameter (pesos) lo aprende el modelo.
- **Accuracy con clases desbalanceadas**: un modelo que dice "no fraude" siempre puede tener 99% accuracy y ser inútil → mirar precision/recall/F1.
- **Inference type**: "millones de registros cada noche" → batch; "respuesta inmediata al usuario" → real-time; "tráfico esporádico e impredecible" → serverless.
- **ML tradicional vs FM**: predicción tabular acotada y explicable → ML tradicional; generación o comprensión abierta de contenido → FM.
- **Bedrock vs SageMaker AI**: consumir FMs por API con poca operación → Bedrock; controlar el entrenamiento, la infraestructura o el ciclo ML → SageMaker AI.
- **Strands vs AgentCore**: Strands construye la lógica del agente; AgentCore aporta runtime y servicios operativos gestionados.
- **¿Cuándo NO usar ML?**: si el problema se resuelve con lógica determinista simple o no hay datos, la respuesta correcta es no usar ML.

## 10. Mini-escenarios de repaso (formato examen)

- *"Una aseguradora quiere predecir el importe de las reclamaciones del próximo trimestre con datos tabulares y necesita explicar cada decisión."* → Regresión con ML tradicional en SageMaker AI.
- *"Agrupar tickets de soporte en temas sin categorías predefinidas."* → Unsupervised learning (clustering).
- *"Extraer importes y campos de facturas escaneadas en PDF."* → Amazon Textract.
- *"Analizar el sentimiento de reseñas de producto sin equipo de ML."* → Amazon Comprehend.
- *"Convertir los podcasts de la empresa en artículos de texto."* → Amazon Transcribe.
- *"Dar voz natural a un asistente telefónico."* → Amazon Polly (+ Lex para la conversación).
- *"Buscar en miles de documentos internos con preguntas en lenguaje natural."* → Amazon Kendra.
- *"Recomendar películas según el historial de cada usuario."* → Amazon Personalize.
- *"Que un humano revise las predicciones con confianza < 80%."* → Amazon A2I.
- *"Resumir y responder preguntas abiertas sobre contratos mediante una API gestionada."* → Foundation model en Amazon Bedrock.
- *"Investigar un mercado, consultar herramientas y preparar un informe en varios pasos."* → Sistema agéntico; Amazon Quick para el workspace gestionado o Strands + AgentCore para una solución propia.
- *"Aplicar siempre el mismo descuento según una tabla legal cerrada."* → Reglas deterministas, no ML.
- *"El modelo rinde 99% en training y 60% en test."* → Overfitting; regularización/más datos/early stopping.
- *"El equipo quiere entrenar, tunear y desplegar un modelo propio end-to-end."* → Amazon SageMaker AI.

## 11. Glosario rápido

| Término | Definición de examen |
|---|---|
| Feature | Variable de entrada del modelo |
| Label | Valor objetivo que se quiere predecir (supervised) |
| Feature engineering | Crear/transformar features para mejorar el modelo |
| Training set | Datos con los que aprende el modelo |
| Validation set | Datos para ajustar hyperparameters |
| Test set | Datos nunca vistos para evaluar generalización |
| Epoch | Una pasada completa por el training set |
| Learning rate | Hyperparameter: tamaño del paso de actualización |
| Inference | Usar el modelo entrenado para predecir |
| Data drift | Los datos de producción cambian respecto a los de training |
| Model drift | La calidad del modelo se degrada con el tiempo |
| Confusion matrix | Tabla TP/FP/TN/FN de un clasificador |
| Ensemble | Combinar varios modelos para mejorar el resultado |
| Transfer learning | Reutilizar un modelo preentrenado en una tarea nueva |
| MLOps | DevOps aplicado al ciclo de vida ML |

## 12. Checklist antes del examen

- [ ] Explico la relación entre AI, ML y DL, y por qué GenAI y agentic AI describen capacidades o patrones distintos.
- [ ] Distingo supervised / unsupervised / semi-supervised / RL con un ejemplo de cada.
- [ ] Distingo clasificación vs regresión vs clustering por el enunciado.
- [ ] Sé cuándo elegir precision y cuándo recall (coste del FP vs FN).
- [ ] Explico overfitting vs underfitting y cómo mitigarlos.
- [ ] Sé qué hace cada servicio de AI gestionado en alcance (Comprehend, Rekognition, Textract, Transcribe, Polly, Translate, Lex, Kendra y Personalize).
- [ ] Elijo entre ML tradicional y foundation models según tarea, explicabilidad, coste y operación.
- [ ] Distingo Bedrock, SageMaker AI, JumpStart, Amazon Q, Amazon Quick, Kiro, Strands Agents y AgentCore.
- [ ] Elijo bien entre real-time, batch, async y serverless inference.
- [ ] Recuerdo que "least operational overhead" apunta al servicio gestionado.

## Mapeo al repo

Este dominio se corresponde con el **módulo 1 (Fundamentos LLM y APIs)** y la parte de evaluación del **módulo 2**.

---

## Fuentes oficiales verificadas

- [Guía oficial AWS Certified AI Practitioner (AIF-C01)](https://docs.aws.amazon.com/aws-certification/latest/ai-practitioner-01/ai-practitioner-01.html)
- [Objetivos del Dominio 1](https://docs.aws.amazon.com/aws-certification/latest/ai-practitioner-01/ai-practitioner-01-domain1.html)
- [Cambios de la revisión 1.1](https://docs.aws.amazon.com/aws-certification/latest/ai-practitioner-01/aif-01-revisions.html)
- [Servicios AWS actualmente en alcance](https://docs.aws.amazon.com/aws-certification/latest/ai-practitioner-01/aif-01-in-scope-services.html)

> ⚠️ **Nota**: los contenidos, pesos y servicios pueden cambiar. Esta guía fue contrastada el
> **21 de agosto de 2026**; revisa la documentación oficial antes de presentarte.
