# NCA-GENL — Guía por áreas del blueprint y temas

Guía del examen **NVIDIA Certified Associate: Generative AI LLMs (NCA-GENL)**. NVIDIA publica
cinco áreas ponderadas en el blueprint y, además, diez temas cubiertos. Los temas desarrollan el
contenido; no son diez dominios con el mismo peso.

> Verificado el 21 de agosto de 2026 contra la
> [página oficial de NCA-GENL](https://www.nvidia.com/en-us/learn/certification/generative-ai-llm-associate/).
> NVIDIA puede cambiar blueprint y formato: vuelve a comprobarlos antes de reservar.

| Área ponderada oficial | Peso | Temas de estudio principales en esta guía |
|---|---:|---|
| Core Machine Learning and AI Knowledge | 30% | Temas 1, 2 y fundamentos del 3 |
| Software Development | 24% | Temas 8, 9 y 10 |
| Experimentation | 22% | Temas 5, 6 y 7 |
| Data Analysis and Visualization | 14% | Tema 4 |
| Trustworthy AI | 10% | Alignment, guardrails, seguridad y uso responsable de los temas 3 y 10 |

---

## Tema 1 — Fundamentals of Machine Learning and Neural Networks

### Tipos de aprendizaje

- **Supervised learning**: datos etiquetados; clasificación (etiqueta discreta) y regresión (valor continuo).
- **Unsupervised learning**: sin etiquetas; clustering (K-means), reducción de dimensionalidad (PCA, t-SNE).
- **Self-supervised learning**: la señal de entrenamiento sale de los propios datos. Es como se pre-entrenan los LLMs (predecir el siguiente token).
- **Reinforcement learning**: agente, entorno, recompensa. Base de RLHF.

### Redes neuronales

- **Neurona**: suma ponderada + bias + función de activación (ReLU, GELU, sigmoid, tanh, softmax en la capa de salida de clasificación).
- **Backpropagation**: calcula gradientes de la loss respecto a los pesos con la regla de la cadena; **gradient descent** (y variantes: SGD, Adam, AdamW) actualiza los pesos.
- **Loss functions**: cross-entropy para clasificación y modelado de lenguaje; MSE para regresión.
- **Learning rate**: hiperparámetro clave; demasiado alto diverge, demasiado bajo no converge. Schedulers: warmup + cosine decay es el estándar en LLMs.
- **Overfitting**: el modelo memoriza el train set y generaliza mal. Mitigación: regularización (L2, dropout), early stopping, más datos, data augmentation.
- **Underfitting**: el modelo es demasiado simple; alta loss también en train.

### Arquitectura Transformer (cae seguro)

- Introducida en *Attention Is All You Need* (2017). Sustituye la recurrencia (RNN/LSTM) por **self-attention**: cada token atiende a todos los demás en paralelo.
- **Self-attention**: Q (query), K (key), V (value); `softmax(QKᵀ/√d)·V`. El escalado por √d estabiliza los gradientes.
- **Multi-head attention**: varias cabezas atienden a subespacios distintos de representación.
- **Positional encoding/embeddings**: aportan orden a la secuencia (el attention es invariante al orden). Variantes modernas: RoPE, ALiBi.
- Variantes: **encoder-only** (BERT — entendimiento, clasificación), **decoder-only** (GPT, Llama — generación autoregresiva), **encoder-decoder** (T5 — traducción, seq2seq).
- **Causal masking** en decoders: cada token solo ve los anteriores.
- Ventaja clave sobre RNN: paralelización total en entrenamiento y mejor manejo de dependencias largas.

### Tokenización y embeddings

- **Tokenización**: texto → tokens (subpalabras). Algoritmos: **BPE** (GPT, Llama), **WordPiece** (BERT), **SentencePiece/Unigram** (T5). Subword equilibra vocabulario manejable y cobertura de palabras raras.
- **Embeddings**: vectores densos que capturan semántica; distancia coseno mide similitud. Base del retrieval semántico y de RAG.
- **Context window**: máximo de tokens que el modelo procesa de una vez.

### GPU y CUDA (stack NVIDIA)

- **CUDA**: plataforma de computación paralela de NVIDIA; permite ejecutar miles de threads en la GPU. El deep learning es esencialmente multiplicación de matrices masivamente paralela → la GPU (miles de cores, alto ancho de banda de memoria) supera con mucho a la CPU en throughput.
- **cuDNN**: librería de primitivas de deep learning optimizadas (convoluciones, attention) sobre CUDA. PyTorch/TensorFlow la usan por debajo.
- **Tensor Cores**: unidades de hardware para multiplicación de matrices en precisión mixta (FP16/BF16/FP8) — mucho más rápidas que FP32.
- **Mixed precision training**: entrenar en FP16/BF16 con acumulación en FP32; ahorra memoria y acelera sin perder calidad.
- **DGX**: sistemas de NVIDIA con múltiples GPUs interconectadas (NVLink) para entrenamiento a gran escala.

### Conceptos de escala y entrenamiento distribuido

- **Data parallelism**: cada GPU tiene una copia completa del modelo y procesa un shard del batch; los gradientes se promedian (all-reduce).
- **Tensor parallelism**: las matrices de cada capa se parten entre GPUs (necesario cuando el modelo no cabe en una).
- **Pipeline parallelism**: capas distintas en GPUs distintas, procesando micro-batches en cadena.
- **Scaling laws**: la loss mejora de forma predecible al escalar parámetros, datos y cómputo de forma conjunta.
- **NVLink**: interconexión de alta velocidad entre GPUs NVIDIA; clave para el paralelismo multi-GPU (sistemas DGX).

### Trampas de examen

- Self-attention ≠ recurrencia: el transformer NO procesa secuencialmente en entrenamiento.
- BERT no genera texto libre (encoder-only); GPT sí (decoder-only).
- Overfitting se detecta comparando métricas de train vs validation, no mirando solo train.
- La GPU acelera por paralelismo de datos/matrices, no por "mayor frecuencia de reloj".
- Softmax es la activación típica de la capa de SALIDA en clasificación multiclase; ReLU/GELU van en las capas ocultas.
- El embedding de un token no es fijo por palabra en un LLM: las capas de attention producen representaciones contextuales.

---

## Tema 2 — Prompt Engineering

### Técnicas base

- **Zero-shot**: solo la instrucción, sin ejemplos.
- **Few-shot / in-context learning**: se incluyen ejemplos entrada→salida en el prompt; el modelo aprende el patrón sin actualizar pesos.
- **Chain-of-thought (CoT)**: pedir razonamiento paso a paso ("Let's think step by step"); mejora tareas de razonamiento aritmético/lógico.
- **Self-consistency**: muestrear varias cadenas de razonamiento y votar la respuesta mayoritaria.
- **System prompt**: instrucciones de rol/comportamiento que condicionan toda la conversación; separado del turno del usuario.
- **Delimitadores y estructura**: separar instrucción, contexto y datos (XML tags, ###) reduce ambigüedad y prompt injection.

### Parámetros de generación

- **Temperature**: reescala la distribución de probabilidad. Baja (→0) = determinista/greedy; alta = más diversidad y más riesgo de alucinación.
- **Top-k**: muestrea solo entre los k tokens más probables.
- **Top-p (nucleus)**: muestrea del conjunto mínimo cuya probabilidad acumulada ≥ p.
- **Max tokens**: límite de longitud de salida (no de calidad).
- **Frequency/presence penalties**: reducen repetición.
- Regla práctica: tareas factuales/extracción → temperature baja; brainstorming/creatividad → alta.

### Técnicas avanzadas y patrones

- **ReAct**: alternar razonamiento (thought) y acciones (tool calls) con observaciones; base de los agentes.
- **Prompt chaining**: descomponer la tarea en varios prompts encadenados (extraer → transformar → redactar).
- **Retrieval-augmented prompting**: inyectar contexto recuperado (RAG) en el prompt y pedir respuesta grounded con citas.
- **Output constraints**: pedir JSON con schema, listas cerradas de valores, o usar structured output del proveedor.
- **Prompt templates y versionado**: tratar los prompts como artefactos versionados y evaluados (datasets de test de prompts, A/B testing).
- **Defensa frente a prompt injection**: separar instrucciones de datos con delimitadores, tratar el contenido recuperado como no confiable, validar salidas.

### Trampas de examen

- Few-shot NO actualiza los pesos del modelo (eso es fine-tuning).
- Temperature 0 no garantiza corrección factual, solo (casi) determinismo.
- CoT ayuda en razonamiento, no necesariamente en recuperación de hechos.
- Prompt engineering es la opción más barata/rápida de adaptación; fine-tuning solo cuando el prompting no llega.
- Los ejemplos few-shot consumen context window (y coste por token) en CADA llamada.
- Escalera de adaptación típica en el examen: prompt engineering → RAG → fine-tuning → pre-training desde cero (de más barato a más caro).

---

## Tema 3 — Alignment

### Por qué

Un LLM pre-entrenado solo predice el siguiente token; alignment lo hace **helpful, honest, harmless** y capaz de seguir instrucciones.

### Pipeline clásico

1. **Pre-training**: self-supervised sobre corpus masivo (predecir siguiente token).
2. **SFT (Supervised Fine-Tuning)** / instruction tuning: pares instrucción→respuesta de calidad.
3. **RLHF (Reinforcement Learning from Human Feedback)**: humanos ordenan respuestas por preferencia → se entrena un **reward model** → se optimiza la policy con **PPO** contra ese reward (con penalización KL para no alejarse del modelo SFT).
4. Alternativas: **DPO (Direct Preference Optimization)** — optimiza directamente sobre pares preferidos/rechazados sin reward model explícito ni RL; más simple y estable. **RLAIF**: el feedback lo da otro modelo IA. **Constitutional AI**: el modelo critica y revisa sus salidas según principios escritos.

### Seguridad y guardrails

- **Guardrails**: filtros/validaciones en entrada y salida (temas prohibidos, PII, jailbreaks). En el stack NVIDIA: **NeMo Guardrails** — toolkit open-source para definir rails programables de conversación (temas, seguridad, llamadas a herramientas).
- **Red teaming**: ataques deliberados para descubrir fallos antes de producción.
- Riesgos: **jailbreaks**, **prompt injection**, sesgo, toxicidad, fuga de datos de entrenamiento.
- **Hallucinations**: salida fluida pero falsa; mitigación con RAG, grounding, citación de fuentes y evaluación.

### Fine-tuning como herramienta de alignment y adaptación

- **Full fine-tuning**: actualiza todos los pesos; máxima capacidad de adaptación, máximo coste y riesgo de **catastrophic forgetting**.
- **PEFT (parameter-efficient fine-tuning)**: LoRA/QLoRA, prompt tuning, adapters; entrena una fracción mínima de parámetros.
- **Instruction tuning**: SFT sobre pares instrucción→respuesta de muchas tareas; enseña a seguir instrucciones en general.
- Cuándo NO fine-tunear: si el problema es de conocimiento actualizable (→ RAG) o de formato/estilo alcanzable con prompting.

### Trampas de examen

- RLHF entrena un reward model desde comparaciones humanas, no desde etiquetas absolutas.
- DPO ≠ RLHF con otro nombre: DPO elimina el reward model y el bucle de RL.
- SFT viene antes de RLHF, no al revés.
- Guardrails complementan el alignment del modelo, no lo sustituyen.
- Alignment reduce comportamientos dañinos pero no garantiza factualidad: un modelo alineado también alucina.

---

## Tema 4 — Data Analysis and Visualization

- **pandas**: DataFrames; `describe()`, `groupby()`, `value_counts()`, manejo de nulos (`isna()`, `fillna()`, `dropna()`). Herramienta estándar de EDA (exploratory data analysis).
- **NumPy**: arrays n-dimensionales, operaciones vectorizadas; base numérica de todo el stack.
- **matplotlib / seaborn**: visualización. Elegir el gráfico correcto:
  - **Histograma**: distribución de una variable numérica.
  - **Box plot**: mediana, cuartiles y **outliers**.
  - **Scatter plot**: relación entre dos variables numéricas (correlación visual).
  - **Bar chart**: comparación entre categorías.
  - **Line chart**: series temporales / curvas de entrenamiento (loss vs epoch).
  - **Heatmap**: matrices de correlación, matrices de confusión, mapas de attention.
- **Estadística básica**: media vs mediana (la mediana resiste outliers), desviación estándar, percentiles, **correlación ≠ causalidad**, correlación de Pearson (lineal) vs Spearman (monótona).
- En LLMs: analizar distribución de longitudes de secuencia (para elegir max length y estrategia de truncado/padding), balance de clases, calidad/duplicados del corpus.
- **RAPIDS / cuDF** (stack NVIDIA): pandas-like acelerado en GPU para datasets grandes.

### Flujo de EDA típico (cae como escenario)

1. `df.info()` / `df.describe()`: tipos, nulos, rangos.
2. Nulos y duplicados: cuantificar antes de decidir imputación o borrado.
3. Distribuciones univariantes (histogramas) y outliers (box plots).
4. Relaciones bivariantes (scatter, heatmap de correlación).
5. Documentar hallazgos que condicionan el preprocesado (features constantes, cardinalidad alta, desbalance de clases).

### Trampas de examen

- Para ver outliers: box plot (no bar chart).
- Para distribución de una sola variable: histograma (no scatter).
- Alta correlación no implica causalidad.
- Pie charts casi nunca son la respuesta correcta: comparaciones → bar chart; evolución temporal → line chart.
- Curvas de entrenamiento (loss vs step/epoch) se visualizan con line charts (TensorBoard/W&B).

---

## Tema 5 — Experimentation

### Métricas de evaluación

- Clasificación: **accuracy** (engañosa con clases desbalanceadas), **precision** (de lo predicho positivo, cuánto es correcto), **recall** (de lo real positivo, cuánto se detecta), **F1** (media armónica), **matriz de confusión**, ROC-AUC.
- Modelado de lenguaje: **perplexity** — exponencial de la cross-entropy media; más baja = el modelo predice mejor el corpus. Compara modelos sobre el mismo tokenizer/corpus.
- Generación de texto:
  - **BLEU**: precisión de n-gramas vs referencia (histórico en traducción).
  - **ROUGE**: recall de n-gramas/subsecuencias vs referencia (resumen). ROUGE-N, ROUGE-L (longest common subsequence).
  - **BERTScore**: similitud semántica con embeddings, no solo overlap literal.
  - **Human evaluation** y **LLM-as-a-judge**: para calidad abierta (helpfulness, coherencia) donde las métricas automáticas se quedan cortas.
- Benchmarks de LLMs: MMLU (conocimiento multitarea), HellaSwag (sentido común), HumanEval (código), TruthfulQA (veracidad).

### Metodología

- **Train/validation/test split**: entrenar / ajustar hiperparámetros y early stopping / evaluación final una sola vez. Nunca ajustar contra test.
- **Cross-validation** (k-fold): estimación más robusta con datos escasos (raro en pre-training LLM por coste, común en ML clásico).
- **Data leakage**: información del test contamina el train (duplicados, contaminación de benchmarks en corpus de pre-training) → métricas infladas.
- **Baseline**: comparar siempre contra algo simple antes de atribuir mejoras.
- Curvas de entrenamiento: train loss baja y val loss sube → overfitting.

### Evaluación específica de sistemas RAG

- **Retrieval**: context recall (¿se recuperó lo necesario?), context precision (¿lo recuperado es relevante?), hit rate, MRR.
- **Generación**: faithfulness (¿la respuesta se apoya en el contexto recuperado?), answer relevance.
- Frameworks: RAGAS y evals propias con LLM-as-a-judge; separar siempre el fallo de retrieval del fallo de generación.

### Trampas de examen

- Perplexity solo aplica a modelos de lenguaje probabilísticos, y menor es mejor.
- BLEU ≈ precision-oriented (traducción); ROUGE ≈ recall-oriented (resumen).
- Con 99% de clase negativa, accuracy 99% no dice nada: mirar precision/recall/F1.
- F1 es media ARMÓNICA de precision y recall (castiga el desequilibrio), no la aritmética.
- Recall alto con precision baja = muchos falsos positivos; precision alta con recall bajo = se escapan positivos reales. La pregunta suele pedir cuál priorizar según el coste del error (p. ej. detección de cáncer → recall).

---

## Tema 6 — Data Preprocessing and Feature Engineering

### Preprocesado clásico

- **Limpieza**: nulos (imputación por media/mediana/moda o eliminación), duplicados, outliers.
- **Escalado**: **standardization** (z-score, media 0 y desviación 1) vs **min-max normalization** (rango [0,1]). Necesario para modelos sensibles a escala; se ajusta (fit) SOLO en train para no filtrar información.
- **Encoding categórico**: one-hot (nominal, pocas categorías), label/ordinal encoding (ordinal), embeddings (alta cardinalidad).
- **Feature engineering**: crear variables informativas a partir de las crudas; selección de features (correlación, importancia).
- Datos desbalanceados: oversampling (SMOTE), undersampling, class weights.

### Preprocesado para LLMs

- Pipeline de corpus: **deduplicación** (exacta y fuzzy/MinHash), filtrado de calidad y de idioma, eliminación de PII, descontaminación de benchmarks.
- **Tokenización** como paso de preprocesado: truncation y padding a longitud fija; attention mask para ignorar padding.
- **Chunking** para RAG: trocear documentos (fijo, por frases, semántico) con overlap; el tamaño de chunk afecta al recall del retrieval.
- Formatos de datos para SFT: pares prompt→completion, plantillas de chat (roles system/user/assistant).
- **Data augmentation** en NLP: paráfrasis, back-translation, generación sintética con LLMs.
- **NeMo Curator** (stack NVIDIA): herramientas GPU-aceleradas para curar corpus a escala (dedup, filtrado, PII).

### Embeddings como features

- Texto → embedding (sentence-transformers o API) → feature densa para clasificación, clustering, dedup semántica o retrieval.
- La similitud coseno entre embeddings es la base del semantic search; normalizar vectores cuando el índice lo requiera.

### Trampas de examen

- El scaler se ajusta en train y se aplica a test (fit en todo el dataset = leakage).
- One-hot para categorías sin orden; ordinal encoding solo si hay orden real.
- La deduplicación del corpus mejora la generalización y reduce memorización.
- La attention mask marca qué tokens son reales (1) y cuáles padding (0); sin ella el modelo atiende al relleno.

---

## Tema 7 — Experiment Design

- **Hipótesis medible** antes de experimentar: qué métrica, qué mejora esperada, sobre qué dataset.
- **Cambiar una variable a la vez** (o usar búsqueda estructurada): si cambias modelo, datos y prompt a la vez, no sabes qué causó la mejora.
- **Hyperparameter tuning**: grid search (exhaustivo, caro), random search (más eficiente en alta dimensión), **Bayesian optimization** (modela la superficie y elige el siguiente punto con criterio). Hiperparámetros típicos de fine-tuning: learning rate, batch size, epochs, LoRA rank.
- **A/B testing**: comparar dos variantes en producción con tráfico dividido; necesita significancia estadística (tamaño de muestra suficiente, p-value/intervalos).
- **Ablation study**: quitar un componente para medir su contribución real.
- **Reproducibilidad**: fijar random seeds, versionar datos/código/configs, registrar experimentos (**MLflow**, **Weights & Biases**, TensorBoard para curvas).
- **Early stopping**: parar cuando la métrica de validation deja de mejorar (patience).
- Coste: estimar GPU-hours; empezar con modelos/datasets pequeños para iterar rápido y escalar lo que funciona.

### Hiperparámetros clave de fine-tuning de LLMs

- **Learning rate**: el más sensible; para fine-tuning se usan valores mucho menores que en pre-training (p. ej. 1e-5–2e-4 con LoRA).
- **Batch size** (y gradient accumulation cuando no cabe en memoria).
- **Epochs**: pocos (1–3 típico en SFT); más epochs → riesgo de overfitting/olvido catastrófico.
- **LoRA rank (r) y alpha**: capacidad del adaptador vs memoria.
- **Warmup ratio y scheduler**: estabilizan el arranque del entrenamiento.

### Trampas de examen

- Random search suele batir a grid search con el mismo presupuesto cuando pocas dimensiones importan.
- El test set se usa una vez al final; la selección de hiperparámetros va contra validation.
- Un ablation mide contribución de componentes; un A/B test compara variantes completas en producción.
- Un experimento sin hipótesis ni métrica previa no es un experimento: es exploración (válida, pero no concluyente).

---

## Tema 8 — Software Development

- **Git**: branches, merge/rebase, pull requests, code review. Versionar también configs y (con DVC o similar) datos/modelos.
- **Entornos**: `venv`/`conda`, `requirements.txt`/`pyproject.toml` con versiones pinneadas para reproducibilidad.
- **Testing**: `pytest`; unit tests (funciones puras: parsers, chunkers), integration tests (pipeline completo), y tests de comportamiento del modelo (evals como tests de regresión). Mockear APIs de LLM en unit tests para coste/determinismo.
- **CI/CD**: pipelines (GitHub Actions, GitLab CI) que ejecutan lint + tests + evals en cada cambio; CD para desplegar modelos/servicios.
- **Contenedores**: **Docker** empaqueta código+dependencias+drivers de usuario; imágenes base de **NGC** (NVIDIA GPU Cloud) traen CUDA/cuDNN/frameworks ya optimizados y versionados. `nvidia-container-toolkit` expone la GPU al contenedor. **Kubernetes** orquesta a escala (con GPU operator).
- **Calidad de código**: PEP 8, type hints, linters (ruff/flake8), formatters (black), docstrings.
- **Logging y manejo de errores**: logging estructurado, retries con backoff ante rate limits de APIs, timeouts.
- **Secretos**: API keys en variables de entorno o secret managers, nunca hardcodeadas ni commiteadas.

### Buenas prácticas específicas de proyectos LLM

- Versionar prompts junto al código (o en un registry) y cubrirlos con evals de regresión en CI.
- Registrar coste por request y tokens consumidos como métrica de primera clase.
- Validar y sanear salidas del modelo antes de usarlas (parsear JSON con schema, no con regex frágiles).
- Feature flags / canary para desplegar cambios de modelo o de prompt gradualmente.

### Trampas de examen

- Docker garantiza reproducibilidad de entorno; no acelera el modelo por sí mismo.
- Las imágenes NGC son la vía recomendada para entornos GPU consistentes.
- Las API keys nunca van en el código fuente ni en el repo.
- Unit test ≠ eval del modelo: el primero valida tu código con mocks; el segundo valida el comportamiento del modelo con datasets.

---

## Tema 9 — Python Libraries for LLMs

- **PyTorch**: framework de deep learning dominante en LLMs; tensores, autograd, `nn.Module`, DataLoader; `.to("cuda")` mueve tensores/modelos a GPU.
- **Hugging Face Transformers**: `AutoTokenizer`, `AutoModelForCausalLM`, `pipeline()` para inferencia rápida, `Trainer` para fine-tuning. **Hub** de modelos/pesos pre-entrenados.
- **Hugging Face Datasets**: carga y procesado eficiente de datasets (`map`, streaming).
- **PEFT**: fine-tuning eficiente en parámetros — **LoRA** (matrices low-rank sobre pesos congelados; se entrena <1% de parámetros), **QLoRA** (LoRA sobre modelo cuantizado a 4-bit). Reduce memoria y coste drásticamente frente al full fine-tuning.
- **sentence-transformers**: modelos de embeddings para búsqueda semántica.
- **LangChain / LlamaIndex**: orquestación de aplicaciones LLM — chains, RAG, agentes, conectores a vector stores.
- **Vector databases**: FAISS (librería), Milvus, Pinecone, Chroma, pgvector; búsqueda por similitud (ANN) sobre embeddings.
- **scikit-learn**: ML clásico, splits (`train_test_split`), métricas (`classification_report`), baselines.
- **OpenAI SDK / clientes de API**: patrón request-response con mensajes por roles; streaming de tokens.
- **Stack NVIDIA**: **NeMo** (framework end-to-end para entrenar/customizar LLMs: SFT, PEFT, RLHF, con paralelismo integrado), **RAPIDS/cuDF** (dataframes en GPU), CUDA Python/CuPy.

### Snippets mínimos que conviene reconocer

```python
# Inferencia rápida con Transformers
import os
from transformers import pipeline
model_id = os.getenv("HF_MODEL_ID", "Qwen/Qwen3-4B-Instruct-2507")
gen = pipeline("text-generation", model=model_id, dtype="auto", device_map="auto")
out = gen("Explica CUDA en una frase:", max_new_tokens=50, temperature=0.2)

# Tokenización con padding/truncation y tensores en GPU
from transformers import AutoTokenizer
tok = AutoTokenizer.from_pretrained("bert-base-uncased")
batch = tok(texts, padding=True, truncation=True, max_length=512, return_tensors="pt").to("cuda")

# LoRA con PEFT
from peft import LoraConfig, get_peft_model
model = get_peft_model(base_model, LoraConfig(r=16, lora_alpha=32, task_type="CAUSAL_LM"))
model.print_trainable_parameters()  # ~0.x% del total
```

### Trampas de examen

- LoRA congela los pesos base y entrena adaptadores pequeños; no entrena todo el modelo.
- `Transformers` da modelos y entrenamiento; `LangChain` orquesta aplicaciones sobre modelos ya servidos.
- FAISS busca por similitud de embeddings; no es una base de datos relacional.
- `return_tensors="pt"` devuelve tensores PyTorch; el modelo y sus inputs deben estar en el mismo device (CPU o CUDA).

---

## Tema 10 — LLM Integration and Deployment

### Optimización de inferencia

- **Quantization**: reducir precisión de pesos/activaciones (FP16 → INT8/INT4/FP8): menos memoria, más throughput, con pérdida de calidad generalmente pequeña. Post-training quantization (PTQ) vs quantization-aware training (QAT).
- **Distillation**: entrenar un modelo pequeño (student) que imite a uno grande (teacher).
- **Pruning**: eliminar pesos/estructuras poco importantes.
- **KV cache**: cachear keys/values de tokens ya generados para no recomputarlos en generación autoregresiva; su memoria crece con contexto y batch.
- **Batching**: agrupar peticiones. **In-flight/continuous batching**: incorpora y saca secuencias del batch dinámicamente durante la generación → mucho mejor utilización de GPU que el batching estático.
- Métricas de serving: **latency** (incl. time-to-first-token), **throughput** (tokens/s), coste por 1K tokens; el trade-off latencia-throughput se gestiona con batching.

### Stack NVIDIA de deployment (cae seguro)

- **TensorRT-LLM**: compila/optimiza LLMs para inferencia en GPUs NVIDIA — **kernel fusion**, quantization (INT8/FP8), paged KV cache, **in-flight batching**, tensor parallelism multi-GPU.
- **Triton Inference Server**: servidor de inferencia open-source **multi-framework** (TensorRT, PyTorch, ONNX...); expone HTTP/gRPC, hace **dynamic batching**, sirve múltiples modelos y versiones concurrentemente, métricas para Prometheus. Backend TensorRT-LLM para servir LLMs optimizados.
- **NIM (NVIDIA Inference Microservices)**: microservicios containerizados con modelos ya optimizados y API estándar (compatible OpenAI) para desplegar en cualquier infraestructura con GPU.
- **NGC**: catálogo de contenedores, modelos pre-entrenados y charts Helm optimizados para GPU.
- Alternativas open-source que conviene reconocer: vLLM (PagedAttention), TGI de Hugging Face.

### Integración en aplicaciones

- Patrón API: servicio REST/gRPC delante del modelo; **streaming** (SSE) para mostrar tokens según se generan y mejorar la latencia percibida.
- **RAG** como patrón de integración: retrieval de contexto (vector DB) + generación grounded; actualiza conocimiento sin re-entrenar y reduce alucinaciones.
- Escalado: réplicas + load balancing; autoscaling en Kubernetes; model parallelism (tensor/pipeline) cuando el modelo no cabe en una GPU.
- **Monitoring en producción**: latencia, throughput, tasa de error, coste, y calidad (drift de inputs, feedback de usuarios, evals continuas); logging de prompts/respuestas conforme a privacidad.

### Estimación de memoria (cálculo que cae)

- Regla rápida: parámetros × bytes por parámetro. Un modelo de 7B en FP16 (2 bytes) ≈ 14 GB solo en pesos; en INT8 ≈ 7 GB; en INT4 ≈ 3,5 GB.
- Sumar el KV cache (crece con context length × batch size) y activaciones.
- Si no cabe en una GPU: quantization, tensor parallelism u offloading.

### Trampas de examen

- Quantization reduce memoria y acelera; NO mejora la calidad del modelo.
- Triton = servidor multi-framework; TensorRT-LLM = motor de optimización/runtime para LLMs. Se combinan: TensorRT-LLM como backend de Triton.
- Dynamic/in-flight batching mejora throughput; la latencia por petición puede subir ligeramente (trade-off).
- RAG añade conocimiento externo sin tocar pesos; fine-tuning cambia pesos pero no da acceso a datos en tiempo real.
- Distillation entrena un modelo NUEVO más pequeño; quantization comprime el MISMO modelo.
- Throughput y latencia no son lo mismo: batching agresivo sube tokens/s totales pero puede empeorar la latencia de cada usuario.

---

## Chuleta final del stack NVIDIA (una línea por pieza)

| Pieza | Qué es | Fase |
|---|---|---|
| CUDA | Plataforma de computación paralela en GPU; base de todo el stack | Transversal |
| cuDNN | Primitivas de deep learning optimizadas sobre CUDA | Entrenamiento e inferencia |
| RAPIDS / cuDF | Data science (pandas-like) acelerado en GPU | Datos |
| NeMo | Framework end-to-end para entrenar/customizar LLMs (SFT, PEFT, RLHF) | Entrenamiento |
| NeMo Curator | Curación de corpus a escala (dedup, filtrado, PII) | Datos |
| NeMo Guardrails | Rails programables de seguridad conversacional | Aplicación |
| TensorRT-LLM | Optimización y runtime de inferencia de LLMs (quantization, in-flight batching) | Inferencia |
| Triton Inference Server | Serving multi-framework con dynamic batching y métricas | Inferencia |
| NIM | Microservicios de inferencia containerizados con API estándar | Despliegue |
| NGC | Catálogo de contenedores, modelos y Helm charts | Distribución |
| DGX / NVLink | Sistemas multi-GPU e interconexión de alta velocidad | Infraestructura |

---

## Cómo usar esta guía

1. Estudia los diez temas y etiqueta cada fallo con una de las cinco áreas ponderadas (mapa en el [README](README.md)).
2. Repasa con [flashcards.md](flashcards.md) en sesiones cortas espaciadas.
3. Haz el [simulacro-50-preguntas.md](simulacro-50-preguntas.md) en 60 minutos cronometrados y repasa en el simulador publicado todas las explicaciones, también las de las preguntas que aciertes.
