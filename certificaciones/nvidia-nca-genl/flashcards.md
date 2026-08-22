# NCA-GENL — Flashcards por tema y área del blueprint

Repaso de los diez temas publicados por NVIDIA, mapeados a las cinco áreas ponderadas del
blueprint. Formato pregunta → respuesta: tapa la respuesta y contesta en voz alta.

> Blueprint verificado el 21 de agosto de 2026. Los temas pueden cambiar; verifica la página
> oficial de NVIDIA antes de presentarte.

---

## Tema 1 — Fundamentals of ML and Neural Networks

**P:** ¿Qué diferencia supervised de unsupervised learning?
**R:** Supervised usa datos etiquetados (clasificación, regresión); unsupervised encuentra estructura sin etiquetas (clustering, PCA).

**P:** ¿Con qué paradigma se pre-entrenan los LLMs?
**R:** Self-supervised learning: la etiqueta sale del propio texto (predecir el siguiente token).

**P:** ¿Qué hace backpropagation?
**R:** Calcula los gradientes de la loss respecto a cada peso (regla de la cadena) para que el optimizador (SGD/Adam) los actualice.

**P:** ¿Cómo se detecta overfitting?
**R:** La loss/métrica de train sigue mejorando mientras la de validation empeora o se estanca.

**P:** ¿Qué calcula self-attention?
**R:** softmax(QKᵀ/√d)·V — pondera cuánto atiende cada token a los demás usando queries, keys y values.

**P:** ¿Por qué el transformer necesita positional encodings?
**R:** Porque self-attention es invariante al orden; sin posiciones, la secuencia sería una "bolsa de tokens".

**P:** Encoder-only vs decoder-only: ejemplo y uso de cada uno.
**R:** Encoder-only: BERT, entendimiento/clasificación. Decoder-only: GPT/Llama, generación autoregresiva de texto.

**P:** ¿Qué es BPE?
**R:** Byte-Pair Encoding: tokenización subword que fusiona iterativamente los pares de símbolos más frecuentes; usada por GPT y Llama.

**P:** ¿Por qué las GPUs aceleran el deep learning?
**R:** Miles de cores y gran ancho de banda ejecutan en paralelo las multiplicaciones de matrices; CUDA/cuDNN exponen ese paralelismo a los frameworks.

**P:** ¿Qué son los Tensor Cores?
**R:** Unidades de hardware de las GPUs NVIDIA especializadas en multiplicación de matrices en precisión mixta (FP16/BF16/FP8).

---

## Tema 2 — Prompt Engineering

**P:** ¿Qué es few-shot prompting?
**R:** Incluir ejemplos entrada→salida en el prompt para que el modelo aprenda el patrón en contexto, sin actualizar pesos.

**P:** ¿Qué es chain-of-thought y cuándo ayuda?
**R:** Pedir razonamiento paso a paso antes de la respuesta; mejora tareas de razonamiento aritmético y lógico.

**P:** ¿Qué es self-consistency?
**R:** Generar varias cadenas de razonamiento con sampling y quedarse con la respuesta mayoritaria.

**P:** ¿Qué controla temperature?
**R:** La aleatoriedad del sampling: baja → salida casi determinista; alta → más diversidad (y más riesgo de error).

**P:** ¿Diferencia entre top-k y top-p?
**R:** Top-k muestrea entre los k tokens más probables (número fijo); top-p entre el conjunto mínimo cuya probabilidad acumulada llega a p (tamaño variable).

**P:** ¿Para qué sirve el system prompt?
**R:** Fijar rol, tono y restricciones que condicionan toda la conversación, separado de los turnos del usuario.

**P:** ¿Qué es prompt injection?
**R:** Texto malicioso (en input de usuario o documentos recuperados) que intenta sobrescribir las instrucciones del sistema.

**P:** ¿Qué configuración para una tarea de extracción de datos factual?
**R:** Temperature baja (≈0), instrucciones claras, formato de salida estructurado y delimitadores para los datos.

**P:** ¿Prompt engineering o fine-tuning: cuál se prueba primero y por qué?
**R:** Prompt engineering: es inmediato y barato; fine-tuning solo si el prompting (y RAG) no alcanzan la calidad requerida.

---

## Tema 3 — Alignment

**P:** Ordena las fases: RLHF, pre-training, SFT.
**R:** Pre-training → SFT (instruction tuning) → RLHF.

**P:** ¿Qué es el reward model en RLHF?
**R:** Un modelo entrenado con comparaciones humanas de respuestas que puntúa salidas; la policy se optimiza (PPO) para maximizar esa puntuación.

**P:** ¿Qué simplifica DPO frente a RLHF?
**R:** Optimiza directamente sobre pares de respuestas preferida/rechazada, sin reward model separado ni bucle de reinforcement learning.

**P:** ¿Qué es RLAIF?
**R:** Como RLHF pero el feedback de preferencias lo genera otro modelo de IA en lugar de humanos.

**P:** ¿Qué es Constitutional AI?
**R:** El modelo critica y revisa sus propias salidas según una lista de principios escritos ("constitución"), reduciendo la dependencia de feedback humano dañino.

**P:** ¿Qué es una hallucination y una mitigación típica?
**R:** Salida fluida pero factualmente falsa; se mitiga con RAG/grounding en fuentes, temperature baja y evaluación de factualidad.

**P:** ¿Qué es NeMo Guardrails?
**R:** Toolkit open-source de NVIDIA para definir rails programables en apps conversacionales: temas permitidos, seguridad, jailbreak detection, control de flujo.

**P:** ¿Qué es red teaming?
**R:** Atacar deliberadamente el modelo (jailbreaks, temas sensibles) antes de producción para descubrir y corregir fallos de seguridad.

**P:** ¿Por qué RLHF usa una penalización KL?
**R:** Para que la policy no se aleje demasiado del modelo SFT y evitar reward hacking / degradación del lenguaje.

---

## Tema 4 — Data Analysis and Visualization

**P:** ¿Qué gráfico para ver la distribución de una variable numérica?
**R:** Histograma (o density plot).

**P:** ¿Qué gráfico muestra mediana, cuartiles y outliers de un vistazo?
**R:** Box plot.

**P:** ¿Qué gráfico para la relación entre dos variables numéricas?
**R:** Scatter plot.

**P:** ¿Media o mediana con outliers extremos?
**R:** Mediana: es robusta a outliers; la media se desplaza con ellos.

**P:** ¿Qué hace `df.groupby("col").mean()` en pandas?
**R:** Agrupa filas por valores de `col` y calcula la media de las demás columnas numéricas por grupo.

**P:** ¿Correlación implica causalidad?
**R:** No: puede haber confounders o coincidencia; la causalidad exige experimentos controlados.

**P:** ¿Para qué analizarías la distribución de longitudes de secuencia de un corpus?
**R:** Para elegir max sequence length y estrategia de truncation/padding sin cortar demasiado contenido ni desperdiciar cómputo.

**P:** ¿Qué es cuDF?
**R:** Librería de RAPIDS con API tipo pandas ejecutada en GPU, para acelerar análisis de datasets grandes.

**P:** ¿Qué visualización usarías para una matriz de confusión?
**R:** Heatmap.

---

## Tema 5 — Experimentation

**P:** ¿Qué es perplexity y qué indica un valor bajo?
**R:** Exponencial de la cross-entropy media; más baja = el modelo asigna más probabilidad al texto real (predice mejor).

**P:** BLEU vs ROUGE: ¿orientación y uso típico de cada una?
**R:** BLEU: precisión de n-gramas, traducción. ROUGE: recall de n-gramas/subsecuencias, resumen.

**P:** ¿Qué aporta BERTScore sobre BLEU/ROUGE?
**R:** Mide similitud semántica con embeddings contextuales, no solo solapamiento literal de n-gramas.

**P:** ¿Precision y recall: definición corta de cada una?
**R:** Precision: de lo que predije positivo, cuánto era correcto. Recall: de lo realmente positivo, cuánto detecté.

**P:** ¿Por qué accuracy engaña con clases desbalanceadas?
**R:** Predecir siempre la clase mayoritaria da accuracy alta sin detectar nada; usar precision/recall/F1.

**P:** ¿Para qué sirve el validation set (vs test)?
**R:** Ajustar hiperparámetros y early stopping; el test se reserva para la evaluación final, una sola vez.

**P:** ¿Qué es data leakage?
**R:** Información del test/futuro se cuela en el entrenamiento (duplicados, contaminación de benchmarks) e infla las métricas.

**P:** ¿Qué es LLM-as-a-judge?
**R:** Usar un LLM potente para puntuar salidas de otro modelo con una rúbrica; escala la evaluación de calidad abierta.

**P:** Train loss baja, validation loss sube: ¿diagnóstico y remedio?
**R:** Overfitting; early stopping, regularización, más datos.

---

## Tema 6 — Data Preprocessing and Feature Engineering

**P:** Standardization vs min-max normalization.
**R:** Standardization: media 0, desviación 1 (z-score). Min-max: reescala a [0,1]. Ambas se ajustan solo con train.

**P:** ¿Por qué el scaler se ajusta solo en train?
**R:** Ajustarlo con test filtra estadísticas del test al entrenamiento (data leakage).

**P:** ¿Cuándo one-hot y cuándo ordinal encoding?
**R:** One-hot para categorías sin orden (nominal); ordinal solo cuando existe un orden real entre categorías.

**P:** ¿Qué es SMOTE?
**R:** Técnica de oversampling que sintetiza ejemplos de la clase minoritaria interpolando entre vecinos, para datasets desbalanceados.

**P:** ¿Qué hacen truncation y padding en tokenización?
**R:** Truncation corta secuencias largas al máximo permitido; padding rellena las cortas hasta longitud fija; la attention mask ignora el padding.

**P:** ¿Por qué deduplicar el corpus de pre-training?
**R:** Reduce memorización, mejora generalización y evita sobre-representar contenido repetido.

**P:** ¿Qué es chunking en RAG y por qué importa el tamaño?
**R:** Trocear documentos en fragmentos indexables; chunks demasiado grandes diluyen la relevancia y demasiado pequeños pierden contexto.

**P:** ¿Qué es NeMo Curator?
**R:** Herramienta NVIDIA GPU-acelerada para curar corpus a escala: deduplicación, filtrado de calidad/idioma, eliminación de PII.

**P:** ¿Qué es back-translation?
**R:** Data augmentation en NLP: traducir a otro idioma y volver, generando paráfrasis del texto original.

---

## Tema 7 — Experiment Design

**P:** ¿Por qué cambiar una sola variable por experimento?
**R:** Si cambias varias a la vez no puedes atribuir la mejora/empeoramiento a ninguna en concreto.

**P:** Grid search vs random search: ¿cuál rinde mejor con presupuesto fijo y por qué?
**R:** Random search, porque explora más valores de las dimensiones que realmente importan en espacios de alta dimensión.

**P:** ¿Qué aporta Bayesian optimization?
**R:** Modela la relación hiperparámetros→métrica y elige el siguiente punto a probar con criterio, reduciendo evaluaciones caras.

**P:** ¿Qué es un ablation study?
**R:** Quitar un componente del sistema (p. ej. el reranker de un RAG) y medir el impacto para conocer su contribución real.

**P:** ¿Qué necesita un A/B test para ser concluyente?
**R:** Asignación aleatoria, métrica definida a priori y muestra suficiente para significancia estadística.

**P:** ¿Qué es early stopping con patience?
**R:** Parar el entrenamiento cuando la métrica de validation lleva N evaluaciones (patience) sin mejorar, quedándose con el mejor checkpoint.

**P:** Nombra tres cosas a fijar/registrar para reproducibilidad.
**R:** Random seeds, versiones de datos/código/configs, y tracking de experimentos (MLflow, W&B).

**P:** ¿Por qué empezar experimentos con modelos/datasets pequeños?
**R:** Iterar barato y rápido para validar la idea antes de gastar GPU-hours en escala completa.

---

## Tema 8 — Software Development

**P:** ¿Por qué pinnear versiones en requirements.txt?
**R:** Reproducibilidad: el mismo código con dependencias distintas puede comportarse diferente o romperse.

**P:** ¿Por qué mockear la API del LLM en unit tests?
**R:** Determinismo, velocidad y coste cero; el modelo real se prueba en integration tests/evals.

**P:** ¿Qué aporta Docker a un proyecto de ML?
**R:** Empaqueta código, dependencias y librerías CUDA de usuario en una imagen reproducible que corre igual en cualquier host.

**P:** ¿Qué es NGC?
**R:** NVIDIA GPU Cloud: catálogo de contenedores, modelos pre-entrenados y Helm charts optimizados para GPU.

**P:** ¿Qué hace falta para que un contenedor Docker vea la GPU?
**R:** Drivers NVIDIA en el host + nvidia-container-toolkit (y pedir la GPU al ejecutar).

**P:** ¿Dónde se guardan las API keys?
**R:** En variables de entorno o un secret manager; nunca hardcodeadas ni commiteadas al repo.

**P:** ¿Qué corre un pipeline de CI típico de un proyecto LLM?
**R:** Lint/format, unit tests, y evals de regresión del modelo/prompts en cada push o PR.

**P:** ¿Qué patrón usar ante rate limits de una API de LLM?
**R:** Retries con exponential backoff (y jitter), más timeouts y manejo explícito de errores.

---

## Tema 9 — Python Libraries for LLMs

**P:** ¿Qué es autograd en PyTorch?
**R:** El motor de diferenciación automática que registra operaciones sobre tensores y calcula gradientes en el backward pass.

**P:** ¿Qué hace `pipeline()` de Hugging Face Transformers?
**R:** Inferencia lista para usar de una tarea (text-generation, sentiment...) encapsulando tokenizer + modelo + post-proceso.

**P:** ¿Qué es LoRA?
**R:** Fine-tuning eficiente: congela los pesos base y entrena matrices low-rank añadidas; entrena <1% de parámetros con calidad cercana al full fine-tuning.

**P:** ¿Qué añade QLoRA sobre LoRA?
**R:** El modelo base se carga cuantizado a 4-bit, reduciendo aún más la memoria necesaria para el fine-tuning.

**P:** ¿Para qué sirve sentence-transformers?
**R:** Generar embeddings de frases/párrafos para búsqueda semántica, clustering y RAG.

**P:** ¿Qué es FAISS?
**R:** Librería de búsqueda de similitud (ANN) sobre vectores densos, usada como índice vectorial en retrieval.

**P:** ¿Qué rol juega LangChain frente a Transformers?
**R:** LangChain orquesta aplicaciones (chains, RAG, agentes, memoria) sobre modelos servidos; Transformers da los modelos y su entrenamiento/inferencia.

**P:** ¿Qué es NVIDIA NeMo?
**R:** Framework end-to-end para construir y customizar LLMs: pre-training, SFT, PEFT, RLHF, con paralelismo multi-GPU integrado.

**P:** ¿Qué hace `model.to("cuda")`?
**R:** Mueve los pesos del modelo a la memoria de la GPU para computar ahí (los tensores de entrada deben ir al mismo device).

---

## Tema 10 — LLM Integration and Deployment

**P:** ¿Qué es quantization y su trade-off?
**R:** Reducir la precisión numérica de pesos/activaciones (FP16→INT8/INT4): menos memoria y más velocidad a cambio de una pérdida de calidad normalmente pequeña.

**P:** ¿Qué es el KV cache?
**R:** Cachear keys/values de los tokens ya procesados para no recomputarlos en cada paso de la generación autoregresiva; consume memoria proporcional a contexto×batch.

**P:** ¿Qué es in-flight (continuous) batching?
**R:** Añadir y retirar secuencias del batch dinámicamente durante la generación, maximizando la utilización de GPU frente al batching estático.

**P:** ¿Qué es TensorRT-LLM?
**R:** Librería de NVIDIA que optimiza LLMs para inferencia: kernel fusion, quantization, paged KV cache, in-flight batching y tensor parallelism.

**P:** ¿Qué es Triton Inference Server?
**R:** Servidor de inferencia open-source multi-framework (TensorRT, PyTorch, ONNX...) con HTTP/gRPC, dynamic batching, multi-modelo y métricas Prometheus.

**P:** ¿Cómo se combinan TensorRT-LLM y Triton?
**R:** TensorRT-LLM optimiza y ejecuta el LLM; Triton lo sirve en producción usando TensorRT-LLM como backend.

**P:** ¿Qué es NVIDIA NIM?
**R:** Microservicios containerizados con modelos ya optimizados y API estándar (compatible OpenAI) para desplegar inferencia en cualquier infra con GPU.

**P:** ¿Qué mide time-to-first-token y por qué importa?
**R:** Latencia hasta el primer token generado; domina la experiencia percibida en aplicaciones con streaming.

**P:** ¿RAG o fine-tuning para que el modelo use datos que cambian a diario?
**R:** RAG: recupera la información actual en cada query sin re-entrenar; el fine-tuning congela conocimiento en los pesos.

**P:** ¿Qué monitorizarías en un LLM en producción?
**R:** Latencia (y TTFT), throughput, tasa de errores, coste por request, y calidad: drift de inputs, evals continuas y feedback de usuarios.
