# NCA-GENL — Blueprint Area and Topic Guide

Exam guide for the **NVIDIA Certified Associate: Generative AI LLMs (NCA-GENL)**. NVIDIA publishes five weighted areas in the blueprint, plus ten topics covered. The topics develop the content; they are not ten domains with equal weight.

> Verified on August 21, 2026 against the
> [official NCA-GENL page](https://www.nvidia.com/en-us/learn/certification/generative-ai-llm-associate/).
> NVIDIA may change the blueprint and format: double-check them before booking.

| Official Weighted Area | Weight | Main Study Topics in This Guide |
|---|---:|---|
| Core Machine Learning and AI Knowledge | 30% | Topics 1, 2, and fundamentals of 3 |
| Software Development | 24% | Topics 8, 9, and 10 |
| Experimentation | 22% | Topics 5, 6, and 7 |
| Data Analysis and Visualization | 14% | Topic 4 |
| Trustworthy AI | 10% | Alignment, guardrails, security, and responsible use from topics 3 and 10 |

---

## Topic 1 — Fundamentals of Machine Learning and Neural Networks

### Types of Learning

- **Supervised learning**: labeled data; classification (discrete label) and regression (continuous value).
- **Unsupervised learning**: without labels; clustering (K-means), dimensionality reduction (PCA, t-SNE).
- **Self-supervised learning**: the training signal comes from the data itself. This is how LLMs are pre-trained (predicting the next token).
- **Reinforcement learning**: agent, environment, reward. Foundation of RLHF.

### Neural Networks

- **Neuron**: weighted sum + bias + activation function (ReLU, GELU, sigmoid, tanh, softmax in the classification output layer).
- **Backpropagation**: calculates gradients of the loss with respect to the weights using the chain rule; **gradient descent** (and variants: SGD, Adam, AdamW) updates the weights.
- **Loss functions**: cross-entropy for classification and language modeling; MSE for regression.
- **Learning rate**: key hyperparameter; too high causes divergence, too low prevents convergence. Schedulers: warmup + cosine decay is the standard in LLMs.
- **Overfitting**: the model memorizes the training set and generalizes poorly. Mitigation: regularization (L2, dropout), early stopping, more data, data augmentation.
- **Underfitting**: the model is too simple; high loss also occurs in training.

### Transformer Architecture (highly likely to appear)

- Introduced in *Attention Is All You Need* (2017). Replaces recurrence (RNN/LSTM) with **self-attention**: each token attends to all others in parallel.
- **Self-attention**: Q (query), K (key), V (value); `softmax(QKᵀ/√d)·V`. Scaling by √d stabilizes gradients.
- **Multi-head attention**: multiple heads attend to different subspaces of representation.
- **Positional encoding/embeddings**: provide order to the sequence (attention is order-invariant). Modern variants: RoPE, ALiBi.
- Variants: **encoder-only** (BERT — understanding, classification), **decoder-only** (GPT, Llama — autoregressive generation), **encoder-decoder** (T5 — translation, seq2seq).
- **Causal masking** in decoders: each token only sees previous ones.
- Key advantage over RNN: full parallelization during training and better handling of long-range dependencies.

### Tokenization and embeddings

- **Tokenization**: text → tokens (subwords). Algorithms: **BPE** (GPT, Llama), **WordPiece** (BERT), **SentencePiece/Unigram** (T5). Subword tokenization balances a manageable vocabulary with coverage of rare words.
- **Embeddings**: dense vectors that capture semantics; cosine distance measures similarity. Foundation of semantic retrieval and RAG.
- **Context window**: maximum number of tokens the model processes at once.

### GPU and CUDA (NVIDIA stack)

- **CUDA**: NVIDIA's parallel computing platform; enables executing thousands of threads on the GPU. Deep learning is essentially massively parallel matrix multiplication → the GPU (thousands of cores, high memory bandwidth) vastly outperforms the CPU in throughput.
- **cuDNN**: optimized deep learning primitive library (convolutions, attention) built on CUDA. PyTorch/TensorFlow use it under the hood.
- **Tensor Cores**: hardware units for mixed-precision (FP16/BF16/FP8) matrix multiplication — much faster than FP32.
- **Mixed precision training**: training in FP16/BF16 with accumulation in FP32; saves memory and accelerates without losing quality.
- **DGX**: NVIDIA systems with multiple interconnected GPUs (NVLink) for large-scale training.

### Scale and distributed training concepts

- **Data parallelism**: each GPU holds a full copy of the model and processes a shard of the batch; gradients are averaged (all-reduce).
- **Tensor parallelism**: matrices of each layer are split across GPUs (necessary when the model doesn't fit on a single GPU).
- **Pipeline parallelism**: different layers on different GPUs, processing micro-batches in a pipeline.
- **Scaling laws**: loss improves predictably when scaling parameters, data, and compute jointly.
- **NVLink**: high-speed interconnect between NVIDIA GPUs; key for multi-GPU parallelism (DGX systems).

### Exam pitfalls

- Self-attention ≠ recurrence: the transformer does NOT process sequentially during training.
- BERT does not generate free text (encoder-only); GPT does (decoder-only).
- Overfitting is detected by comparing train vs. validation metrics, not by looking at train metrics alone.
- The GPU accelerates via data/matrix parallelism, not by "higher clock frequency".
- Softmax is the typical activation for the OUTPUT layer in multi-class classification; ReLU/GELU go in hidden layers.
- A token's embedding is not fixed per word in an LLM: attention layers produce contextual representations.

---

## Topic 2 — Prompt Engineering

### Base techniques

- **Zero-shot**: instruction only, no examples.
- **Few-shot / in-context learning**: input→output examples are included in the prompt; the model learns the pattern without updating weights.
- **Chain-of-thought (CoT)**: asking for step-by-step reasoning ("Let's think step by step"); improves arithmetic/logical reasoning tasks.
- **Self-consistency**: sampling multiple reasoning chains and voting for the majority answer.
- **System prompt**: role/behavior instructions that condition the entire conversation; separated from the user turn.
- **Delimiters and structure**: separating instruction, context, and data (XML tags, ###) reduces ambiguity and prompt injection.

### Generation Parameters

- **Temperature**: rescales the probability distribution. Low (→0) = deterministic/greedy; high = more diversity and higher risk of hallucination.
- **Top-k**: samples only from the k most probable tokens.
- **Top-p (nucleus)**: samples from the minimum set whose cumulative probability is ≥ p.
- **Max tokens**: limits output length (not quality).
- **Frequency/presence penalties**: reduce repetition.
- Rule of thumb: factual/extraction tasks → low temperature; brainstorming/creativity → high.

### Advanced Techniques and Patterns

- **ReAct**: alternating reasoning (thought) and actions (tool calls) with observations; the basis of agents.
- **Prompt chaining**: decomposing the task into several chained prompts (extract → transform → draft).
- **Retrieval-augmented prompting**: injecting retrieved context (RAG) into the prompt and requesting a grounded response with citations.
- **Output constraints**: requesting JSON with a schema, closed lists of values, or using the provider's structured output.
- **Prompt templates and versioning**: treating prompts as versioned and evaluated artifacts (prompt test datasets, A/B testing).
- **Defense against prompt injection**: separating instructions from data with delimiters, treating retrieved content as untrusted, validating outputs.

### Exam Traps

- Few-shot does NOT update model weights (that is fine-tuning).
- Temperature 0 does not guarantee factual correctness, only (near) determinism.
- CoT aids reasoning, not necessarily fact retrieval.
- Prompt engineering is the cheapest/fastest adaptation option; fine-tuning only when prompting is insufficient.
- Few-shot examples consume context window (and token cost) in EVERY call.
- Typical adaptation ladder in the exam: prompt engineering → RAG → fine-tuning → pre-training from scratch (from cheapest to most expensive).

---

## Topic 3 — Alignment

### Why

A pre-trained LLM only predicts the next token; alignment makes it **helpful, honest, harmless** and capable of following instructions.

### Classic Pipeline

1. **Pre-training**: self-supervised on a massive corpus (predicting the next token).
2. **SFT (Supervised Fine-Tuning)** / instruction tuning: high-quality instruction→response pairs.
3. **RLHF (Reinforcement Learning from Human Feedback)**: humans rank responses by preference → a **reward model** is trained → the policy is optimized with **PPO** against that reward (with KL penalty to avoid drifting from the SFT model).
4. Alternatives: **DPO (Direct Preference Optimization)** — optimizes directly on preferred/rejected pairs without an explicit reward model or RL; simpler and more stable. **RLAIF**: feedback is provided by another AI model. **Constitutional AI**: the model critiques and revises its outputs according to written principles.

### Security and guardrails

- **Guardrails**: input/output filters and validations (prohibited topics, PII, jailbreaks). In the NVIDIA stack: **NeMo Guardrails** — an open-source toolkit for defining programmable conversation rails (topics, safety, tool calls).
- **Red teaming**: deliberate attacks to uncover failures before production.
- Risks: **jailbreaks**, **prompt injection**, bias, toxicity, training data leakage.
- **Hallucinations**: fluent but false output; mitigation via RAG, grounding, source citation, and evaluation.

### Fine-tuning as an alignment and adaptation tool

- **Full fine-tuning**: updates all weights; maximum adaptation capability, highest cost, and risk of **catastrophic forgetting**.
- **PEFT (parameter-efficient fine-tuning)**: LoRA/QLoRA, prompt tuning, adapters; trains only a minimal fraction of parameters.
- **Instruction tuning**: SFT on instruction→response pairs across many tasks; teaches the model to follow instructions generally.
- When NOT to fine-tune: if the problem is updatable knowledge (→ RAG) or format/style achievable via prompting.

### Exam traps

- RLHF trains a reward model from human comparisons, not from absolute labels.
- DPO ≠ RLHF under another name: DPO eliminates the reward model and the RL loop.
- SFT comes before RLHF, not the other way around.
- Guardrails complement model alignment; they do not replace it.
- Alignment reduces harmful behaviors but does not guarantee factual accuracy: an aligned model can still hallucinate.

---

## Topic 4 — Data Analysis and Visualization

- **pandas**: DataFrames; `describe()`, `groupby()`, `value_counts()`, null handling (`isna()`, `fillna()`, `dropna()`). Standard EDA (exploratory data analysis) tool.
- **NumPy**: n-dimensional arrays, vectorized operations; the numerical foundation of the entire stack.
- **matplotlib / seaborn**: visualization. Choosing the correct chart:
  - **Histogram**: distribution of a single numerical variable.
  - **Box plot**: median, quartiles, and **outliers**.
  - **Scatter plot**: relationship between two numerical variables (visual correlation).
  - **Bar chart**: comparison across categories.
  - **Line chart**: time series / training curves (loss vs. epoch).
  - **Heatmap**: correlation matrices, confusion matrices, attention maps.
- **Basic statistics**: mean vs. median (median resists outliers), standard deviation, percentiles, **correlation ≠ causation**, Pearson correlation (linear) vs. Spearman (monotonic).
- In LLMs: analyze sequence length distributions (to choose max length and truncation/padding strategy), class balance, corpus quality/duplicates.
- **RAPIDS / cuDF** (NVIDIA stack): GPU-accelerated, pandas-like processing for large datasets.

### Typical EDA workflow (common scenario)

1. `df.info()` / `df.describe()`: types, nulls, ranges.
2. Nulls and duplicates: quantify before deciding on imputation or deletion.
3. Univariate distributions (histograms) and outliers (box plots).
4. Bivariate relationships (scatter plots, correlation heatmaps).
5. Document findings that dictate preprocessing (constant features, high cardinality, class imbalance).

### Exam traps

- To visualize outliers: box plot (not bar chart).
- For the distribution of a single variable: histogram (not scatter plot).
- High correlation does not imply causation.
- Pie charts are almost never the correct answer: for comparisons → bar chart; for temporal evolution → line chart.
- Training curves (loss vs. step/epoch) are visualized with line charts (TensorBoard/W&B).

---

## Topic 5 — Experimentation

### Evaluation Metrics

- Classification: **accuracy** (misleading with imbalanced classes), **precision** (of the predicted positives, how many are correct), **recall** (of the actual positives, how many are detected), **F1** (harmonic mean), **confusion matrix**, ROC-AUC.
- Language modeling: **perplexity** — exponential of the mean cross-entropy; lower is better = the model predicts the corpus better. Compare models on the same tokenizer/corpus.
- Text generation:
  - **BLEU**: n-gram precision vs. reference (historical in translation).
  - **ROUGE**: n-gram/subsequence recall vs. reference (summarization). ROUGE-N, ROUGE-L (longest common subsequence).
  - **BERTScore**: semantic similarity using embeddings, not just literal overlap.
  - **Human evaluation** and **LLM-as-a-judge**: for open-ended quality (helpfulness, coherence) where automatic metrics fall short.
- LLM Benchmarks: MMLU (multitask knowledge), HellaSwag (common sense), HumanEval (code), TruthfulQA (truthfulness).

### Methodology

- **Train/validation/test split**: train / tune hyperparameters and early stopping / final evaluation only once. Never tune against the test set.
- **Cross-validation** (k-fold): more robust estimation with scarce data (rare in LLM pre-training due to cost, common in classical ML).
- **Data leakage**: test information contaminates the train set (duplicates, benchmark contamination in pre-training corpus) → inflated metrics.
- **Baseline**: always compare against something simple before attributing improvements.
- Training curves: train loss decreases and val loss increases → overfitting.

### Specific Evaluation of RAG Systems

- **Retrieval**: context recall (was the necessary information retrieved?), context precision (is the retrieved information relevant?), hit rate, MRR.
- **Generation**: faithfulness (is the answer supported by the retrieved context?), answer relevance.
- Frameworks: RAGAS and custom evals with LLM-as-a-judge; always separate retrieval failure from generation failure.

### Exam Traps

- Perplexity only applies to probabilistic language models, and lower is better.
- BLEU ≈ precision-oriented (translation); ROUGE ≈ recall-oriented (summarization).
- With 99% negative class, 99% accuracy tells you nothing: look at precision/recall/F1.
- F1 is the HARMONIC mean of precision and recall (penalizes imbalance), not the arithmetic mean.
- High recall with low precision = many false positives; high precision with low recall = real positives are missed. The question usually asks which to prioritize based on the cost of error (e.g., cancer detection → recall).

---

## Topic 6 — Data Preprocessing and Feature Engineering

### Classic Preprocessing

- **Cleaning**: nulls (imputation via mean/median/mode or removal), duplicates, outliers.
- **Scaling**: **standardization** (z-score, mean 0 and standard deviation 1) vs **min-max normalization** (range [0,1]). Required for scale-sensitive models; fit ONLY on train data to avoid information leakage.
- **Categorical encoding**: one-hot (nominal, few categories), label/ordinal encoding (ordinal), embeddings (high cardinality).
- **Feature engineering**: creating informative variables from raw data; feature selection (correlation, importance).
- Imbalanced data: oversampling (SMOTE), undersampling, class weights.

### Preprocessing for LLMs

- Corpus pipeline: **deduplication** (exact and fuzzy/MinHash), quality and language filtering, PII removal, benchmark decontamination.
- **Tokenization** as a preprocessing step: truncation and padding to fixed length; attention mask to ignore padding.
- **Chunking** for RAG: splitting documents (fixed, by sentences, semantic) with overlap; chunk size affects retrieval recall.
- Data formats for SFT: prompt→completion pairs, chat templates (system/user/assistant roles).
- **Data augmentation** in NLP: paraphrasing, back-translation, synthetic generation with LLMs.
- **NeMo Curator** (NVIDIA stack): GPU-accelerated tools for curating large-scale corpora (dedup, filtering, PII).

### Embeddings as Features

- Text → embedding (sentence-transformers or API) → dense feature for classification, clustering, semantic deduplication, or retrieval.
- Cosine similarity between embeddings is the basis of semantic search; normalize vectors when the index requires it.

### Exam Traps

- The scaler is fitted on train data and applied to test data (fitting on the entire dataset = leakage).
- One-hot for unordered categories; ordinal encoding only if there is a true order.
- Corpus deduplication improves generalization and reduces memorization.
- The attention mask marks which tokens are real (1) and which are padding (0); without it, the model attends to the padding.

---

## Topic 7 — Experiment Design

- **Measurable hypothesis** before experimenting: which metric, what expected improvement, on which dataset.
- **Change one variable at a time** (or use structured search): if you change the model, data, and prompt simultaneously, you won't know what caused the improvement.
- **Hyperparameter tuning**: grid search (exhaustive, expensive), random search (more efficient in high dimensions), **Bayesian optimization** (models the surface and selects the next point based on criteria). Typical fine-tuning hyperparameters: learning rate, batch size, epochs, LoRA rank.
- **A/B testing**: comparing two variants in production with split traffic; requires statistical significance (sufficient sample size, p-value/intervals).
- **Ablation study**: removing a component to measure its real contribution.
- **Reproducibility**: fixing random seeds, versioning data/code/configs, logging experiments (**MLflow**, **Weights & Biases**, TensorBoard for curves).
- **Early stopping**: stopping when the validation metric stops improving (patience).
- Cost: estimate GPU-hours; start with small models/datasets to iterate quickly and scale what works.

### Key LLM Fine-Tuning Hyperparameters

- **Learning rate**: the most sensitive; for fine-tuning, much lower values are used than in pre-training (e.g., 1e-5–2e-4 with LoRA).
- **Batch size** (and gradient accumulation when memory is insufficient).
- **Epochs**: few (1–3 typical in SFT); more epochs → risk of overfitting/catastrophic forgetting.
- **LoRA rank (r) and alpha**: adapter capacity vs. memory.
- **Warmup ratio and scheduler**: stabilize the training start.

### Exam Traps

- Random search usually beats grid search with the same budget when few dimensions matter.
- The test set is used once at the end; hyperparameter selection goes against validation.
- An ablation measures the contribution of components; an A/B test compares complete variants in production.
- An experiment without a prior hypothesis or metric is not an experiment: it is exploration (valid, but not conclusive).

---

## Topic 8 — Software Development

- **Git**: branches, merge/rebase, pull requests, code review. Version configs and (with DVC or similar) data/models.
- **Environments**: `venv`/`conda`, `requirements.txt`/`pyproject.toml` with pinned versions for reproducibility.
- **Testing**: `pytest`; unit tests (pure functions: parsers, chunkers), integration tests (full pipeline), and model behavior tests (evals as regression tests). Mock LLM APIs in unit tests for cost/determinism.
- **CI/CD**: pipelines (GitHub Actions, GitLab CI) that run lint + tests + evals on every change; CD to deploy models/services.
- **Containers**: **Docker** packages code+dependencies+user drivers; base images from **NGC** (NVIDIA GPU Cloud) bring CUDA/cuDNN/frameworks already optimized and versioned. `nvidia-container-toolkit` exposes the GPU to the container. **Kubernetes** orchestrates at scale (with GPU operator).
- **Code quality**: PEP 8, type hints, linters (ruff/flake8), formatters (black), docstrings.
- **Logging and error handling**: structured logging, retries with backoff against API rate limits, timeouts.
- **Secrets**: API keys in environment variables or secret managers, never hardcoded or committed.

### Specific Best Practices for LLM Projects

- Version prompts alongside code (or in a registry) and cover them with regression evals in CI.
- Log cost per request and tokens consumed as a first-class metric.
- Validate and sanitize model outputs before using them (parse JSON with schema, not fragile regex).
- Feature flags / canary to deploy model or prompt changes gradually.

### Exam Traps

- Docker guarantees environment reproducibility; it does not accelerate the model itself.
- NGC images are the recommended path for consistent GPU environments.
- API keys never go in source code or in the repo.
- Unit test ≠ model eval: the first validates your code with mocks; the second validates model behavior with datasets.

---

## Topic 9 — Python Libraries for LLMs

- **PyTorch**: dominant deep learning framework for LLMs; tensors, autograd, `nn.Module`, DataLoader; `.to("cuda")` moves tensors/models to GPU.
- **Hugging Face Transformers**: `AutoTokenizer`, `AutoModelForCausalLM`, `pipeline()` for fast inference, `Trainer` for fine-tuning. **Hub** of pre-trained models/weights.
- **Hugging Face Datasets**: efficient loading and processing of datasets (`map`, streaming).
- **PEFT**: parameter-efficient fine-tuning — **LoRA** (low-rank matrices over frozen weights; trains <1% of parameters), **QLoRA** (LoRA on a 4-bit quantized model). Drastically reduces memory and cost compared to full fine-tuning.
- **sentence-transformers**: embedding models for semantic search.
- **LangChain / LlamaIndex**: LLM application orchestration — chains, RAG, agents, connectors to vector stores.
- **Vector databases**: FAISS (library), Milvus, Pinecone, Chroma, pgvector; similarity search (ANN) over embeddings.
- **scikit-learn**: classical ML, splits (`train_test_split`), metrics (`classification_report`), baselines.
- **OpenAI SDK / API clients**: request-response pattern with role-based messages; token streaming.
- **NVIDIA Stack**: **NeMo** (end-to-end framework for training/customizing LLMs: SFT, PEFT, RLHF, with integrated parallelism), **RAPIDS/cuDF** (GPU dataframes), CUDA Python/CuPy.

### Minimal snippets to recognize

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

### Exam traps

- LoRA freezes base weights and trains small adapters; it does not train the entire model.
- `Transformers` provides models and training; `LangChain` orchestrates applications over already served models.
- FAISS searches by embedding similarity; it is not a relational database.
- `return_tensors="pt"` returns PyTorch tensors; the model and its inputs must be on the same device (CPU or CUDA).

---

## Topic 10 — LLM Integration and Deployment

### Inference optimization

- **Quantization**: reduce precision of weights/activations (FP16 → INT8/INT4/FP8): less memory, higher throughput, with generally small quality loss. Post-training quantization (PTQ) vs quantization-aware training (QAT).
- **Distillation**: train a small model (student) to mimic a large one (teacher).
- **Pruning**: remove unimportant weights/structures.
- **KV cache**: cache keys/values of already generated tokens to avoid recomputing them in autoregressive generation; its memory grows with context and batch.
- **Batching**: grouping requests. **In-flight/continuous batching**: dynamically adds and removes sequences from the batch during generation → much better GPU utilization than static batching.
- Serving metrics: **latency** (incl. time-to-first-token), **throughput** (tokens/s), cost per 1K tokens; the latency-throughput trade-off is managed with batching.

### NVIDIA deployment stack (highly likely to appear)

- **TensorRT-LLM**: compiles/optimizes LLMs for inference on NVIDIA GPUs — **kernel fusion**, quantization (INT8/FP8), paged KV cache, **in-flight batching**, multi-GPU tensor parallelism.
- **Triton Inference Server**: open-source **multi-framework** inference server (TensorRT, PyTorch, ONNX...); exposes HTTP/gRPC, performs **dynamic batching**, serves multiple models and versions concurrently, metrics for Prometheus. TensorRT-LLM backend for serving optimized LLMs.
- **NIM (NVIDIA Inference Microservices)**: containerized microservices with pre-optimized models and standard API (OpenAI-compatible) for deployment on any GPU-enabled infrastructure.
- **NGC**: catalog of containers, pre-trained models, and GPU-optimized Helm charts.
- Open-source alternatives to recognize: vLLM (PagedAttention), Hugging Face TGI.

### Integration in applications

- API Pattern: REST/gRPC service in front of the model; **streaming** (SSE) to display tokens as they are generated and improve perceived latency.
- **RAG** as an integration pattern: context retrieval (vector DB) + grounded generation; updates knowledge without re-training and reduces hallucinations.
- Scaling: replicas + load balancing; autoscaling in Kubernetes; model parallelism (tensor/pipeline) when the model does not fit in a single GPU.
- **Production monitoring**: latency, throughput, error rate, cost, and quality (input drift, user feedback, continuous evaluations); prompt/response logging in compliance with privacy.

### Memory Estimation (calculation that falls)

- Quick rule: parameters × bytes per parameter. A 7B model in FP16 (2 bytes) ≈ 14 GB just in weights; in INT8 ≈ 7 GB; in INT4 ≈ 3.5 GB.
- Add the KV cache (grows with context length × batch size) and activations.
- If it does not fit in a single GPU: quantization, tensor parallelism, or offloading.

### Exam Traps

- Quantization reduces memory and accelerates; it does NOT improve model quality.
- Triton = multi-framework server; TensorRT-LLM = optimization/runtime engine for LLMs. They are combined: TensorRT-LLM as Triton's backend.
- Dynamic/in-flight batching improves throughput; per-request latency may increase slightly (trade-off).
- RAG adds external knowledge without touching weights; fine-tuning changes weights but does not provide access to real-time data.
- Distillation trains a NEW smaller model; quantization compresses the SAME model.
- Throughput and latency are not the same: aggressive batching increases total tokens/s but may worsen each user's latency.

---

## NVIDIA Stack Final Cheat Sheet (one line per component)

| Component | What it is | Phase |
|---|---|---|
| CUDA | Parallel computing platform on GPU; foundation of the entire stack | Cross-cutting |
| cuDNN | Optimized deep learning primitives on top of CUDA | Training and inference |
| RAPIDS / cuDF | GPU-accelerated data science (pandas-like) | Data |
| NeMo | End-to-end framework for training/customizing LLMs (SFT, PEFT, RLHF) | Training |
| NeMo Curator | Scale corpus curation (dedup, filtering, PII) | Data |
| NeMo Guardrails | Programmable rails for conversational safety | Application |
| TensorRT-LLM | LLM inference optimization and runtime (quantization, in-flight batching) | Inference |
| Triton Inference Server | Multi-framework serving with dynamic batching and metrics | Inference |
| NIM | Containerized inference microservices with standard API | Deployment |
| NGC | Catalog of containers, models, and Helm charts | Distribution |
| DGX / NVLink | Multi-GPU systems and high-speed interconnection | Infrastructure |

---

## How to use this guide

1. Study the ten topics and tag each failure with one of the five weighted areas (map in the [README](README.md)).
2. Review with [flashcards.md](flashcards.md) in short spaced sessions.
3. Take the [simulacro-50-preguntas.md](simulacro-50-preguntas.md) in 60 minutes and review every explanation in the published simulator, including the questions you answer correctly.
