# Module 08 — Production Engineering for LLM systems

An LLM system that runs on your laptop is not a product. This module covers everything that separates a demo from a production system: observability, continuous evaluation, cost control, Docker packaging, deployment (open-source and AWS), Responsible AI, security, and safety. It is the module that turns what you built in Modules III and IV into something operational.

**Proof of work** (from the [learning path](../RUTA_DE_APRENDIZAJE.md)): the system from modules 03–07 deployed, monitored, and with measured costs.

## Learning Objectives

By the end of this module, you should be able to:

1. Instrument any LLM call with traces, latency/token/cost metrics, and structured logs, and set up observability with LangSmith or Langfuse.
2. Build a prompt regression testing suite that runs in CI and blocks deployments when quality drops.
3. Reduce an LLM system's bill of materials with semantic caching, model routing, and batching, and justify each technique with numbers.
4. Package an LLM API into an optimized Docker image (multi-stage, cacheable layers, non-root) and orchestrate it with docker-compose alongside its observability stack.
5. Make informed choices between vLLM, Ollama, and Triton for serving open-source models, and between ECS Fargate, Lambda, and SageMaker for deploying on AWS.
6. Evaluate bias and fairness in a system, document it (model cards), and explain its decisions.
7. Apply the OWASP Top 10 for LLMs: defend against prompt injection, prevent data leaks, and design the IAM/KMS/network layer an LLM system needs on AWS.
8. Implement guardrails and moderation before and after the model, and monitor for abuse.

## Module Structure

```
modulo-08-production-engineering/
├── README.md                      ← estás aquí
├── teoria/
│   ├── 01-observabilidad.md
│   ├── 02-evaluacion-continua.md
│   ├── 03-optimizacion-costes.md
│   ├── 04-docker-para-llms.md
│   ├── 05-despliegue-open-source.md
│   ├── 06-aws-despliegue.md
│   ├── 07-responsible-ai.md
│   ├── 08-seguridad-y-governance.md
│   └── 09-safety-en-produccion.md
├── labs/
│   ├── 01_trazas_manuales.py
│   ├── 02_langsmith_tracing.py
│   ├── 03_cache_semantico.py
│   ├── 04_model_routing.py
│   ├── 05_eval_regresion.py
│   ├── 06_ollama_local.py
│   └── 07_prompt_injection.py
├── docker/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── app.py
│   ├── prometheus.yml
│   ├── requirements.txt
│   └── README.md
└── ejercicios.md                  ← enunciados, tests y rúbrica
```

## Preparation

From the repo root:

```bash
uv sync --extra ops        # instala prometheus-client, locust + dependencias base
source .venv/bin/activate
```

The labs load the `.env` from the root with `python-dotenv`. You need at least
`OPENAI_API_KEY`; lab 02 also uses `LANGSMITH_API_KEY` (free in the developer tier)
and requires the extra `agents` (`uv sync --extra ops --extra agents`). Lab 06 requires
[Ollama](https://ollama.com) installed locally. **No lab requires an AWS account**:
all AWS content is covered theoretically with detailed walkthroughs.

## Study order and estimated time (~55 h)

| # | Block | Theory | Lab / practice | Hours |
|---|--------|--------|----------------|-------|
| 1 | LLM Observability | [01-observabilidad.md](teoria/01-observabilidad.md) | [01_trazas_manuales.py](labs/01_trazas_manuales.py), [02_langsmith_tracing.py](labs/02_langsmith_tracing.py) | 8 |
| 2 | Continuous Evaluation | [02-evaluacion-continua.md](teoria/02-evaluacion-continua.md) | [05_eval_regresion.py](labs/05_eval_regresion.py) | 7 |
| 3 | Cost Optimization | [03-optimizacion-costes.md](teoria/03-optimizacion-costes.md) | [03_cache_semantico.py](labs/03_cache_semantico.py), [04_model_routing.py](labs/04_model_routing.py) | 8 |
| 4 | Docker for LLMs | [04-docker-para-llms.md](teoria/04-docker-para-llms.md) | [docker/](docker/README.md) | 6 |
| 5 | Open-source Deployment | [05-despliegue-open-source.md](teoria/05-despliegue-open-source.md) | [06_ollama_local.py](labs/06_ollama_local.py) | 6 |
| 6 | AWS: Deployment and Monitoring | [06-aws-despliegue.md](teoria/06-aws-despliegue.md) | walkthroughs in theory (no AWS account needed) | 6 |
| 7 | Responsible AI | [07-responsible-ai.md](teoria/07-responsible-ai.md) | exercises 8–9 | 5 |
| 8 | Security and Governance | [08-seguridad-y-governance.md](teoria/08-seguridad-y-governance.md) | [07_prompt_injection.py](labs/07_prompt_injection.py) | 6 |
| 9 | Safety in Production | [09-safety-en-produccion.md](teoria/09-safety-en-produccion.md) | exercises 10–12 | 3 |
| — | Exercises and Review | [ejercicios.md](ejercicios.md) | Tests and rubric | — |

Order matters: observability comes first because everything else (evaluation, costs, deployment) relies on the ability to measure. Security and safety come last because they presuppose that you already know how to deploy and monitor what you are protecting.

## How to run the labs

```bash
# Desde la raíz del repo, con el venv activado
python modulo-08-production-engineering/labs/01_trazas_manuales.py
python modulo-08-production-engineering/labs/05_eval_regresion.py; echo "exit code: $?"
```

Each lab is self-contained, uses the current volume tier (`gpt-5.6-luna`, August 2026 catalog), and explains in its docstring what it demonstrates and what you should observe in the output.

## Relationship with certifications

- **AWS AIF-C01**: blocks 6, 7, 8, and 9 directly cover the deployment, Responsible AI, security, and governance domains of the exam. Additional material in
   [`certificaciones/aws-aif-c01/`](../certificaciones/aws-aif-c01/).
- **NVIDIA NCA-GENL**: block 5 (vLLM, Triton) covers the serving and inference domain.
