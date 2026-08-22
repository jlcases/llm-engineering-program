# Módulo V — LLMOps, producción y Responsible AI (2 ECTS)

Un sistema LLM que funciona en tu portátil no es un producto. Este módulo cubre todo lo que
separa una demo de un sistema en producción: observabilidad, evaluación continua, control de
costes, empaquetado con Docker, despliegue (open-source y AWS), Responsible AI, seguridad
y safety. Es el módulo que convierte lo construido en los módulos III y IV en algo operable.

**Hito de salida** (del [plan de estudios](../PLAN_DE_ESTUDIOS.md)): el sistema del módulo III/IV
desplegado, monitorizado y con costes medidos.

## Objetivos de aprendizaje

Al terminar este módulo deberías ser capaz de:

1. Instrumentar cualquier llamada LLM con trazas, métricas de latencia/tokens/coste y logs
   estructurados, y montar observabilidad con LangSmith o Langfuse.
2. Construir una suite de regression testing de prompts que corra en CI y bloquee despliegues
   cuando la calidad cae.
3. Reducir la factura de un sistema LLM con caching semántico, model routing y batching,
   y justificar cada técnica con números.
4. Empaquetar una API LLM en una imagen Docker optimizada (multi-stage, capas cacheables,
   non-root) y orquestarla con docker-compose junto a su stack de observabilidad.
5. Elegir con criterio entre vLLM, Ollama y Triton para servir modelos open-source, y entre
   ECS Fargate, Lambda y SageMaker para desplegar en AWS.
6. Evaluar sesgo y fairness de un sistema, documentarlo (model cards) y explicar sus decisiones.
7. Aplicar el OWASP Top 10 para LLMs: defenderte de prompt injection, evitar fugas de datos
   y diseñar la capa de IAM/KMS/red que un sistema LLM necesita en AWS.
8. Poner guardrails y moderación delante y detrás del modelo, y monitorizar abusos.

## Estructura del módulo

```
modulo-05-llmops/
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

## Preparación

Desde la raíz del repo:

```bash
uv sync --extra ops        # instala prometheus-client, locust + dependencias base
source .venv/bin/activate
```

Los labs cargan el `.env` de la raíz con `python-dotenv`. Necesitas como mínimo
`OPENAI_API_KEY`; el lab 02 usa además `LANGSMITH_API_KEY` (gratuita en el tier developer)
y requiere el extra `agents` (`uv sync --extra ops --extra agents`). El lab 06 requiere
[Ollama](https://ollama.com) instalado en local. **Ningún lab necesita cuenta de AWS**:
todo lo de AWS se trabaja en teoría con walkthroughs detallados.

## Orden de estudio y tiempo estimado (~55 h)

| # | Bloque | Teoría | Lab / práctica | Horas |
|---|--------|--------|----------------|-------|
| 1 | Observabilidad LLM | [01-observabilidad.md](teoria/01-observabilidad.md) | [01_trazas_manuales.py](labs/01_trazas_manuales.py), [02_langsmith_tracing.py](labs/02_langsmith_tracing.py) | 8 |
| 2 | Evaluación continua | [02-evaluacion-continua.md](teoria/02-evaluacion-continua.md) | [05_eval_regresion.py](labs/05_eval_regresion.py) | 7 |
| 3 | Optimización de costes | [03-optimizacion-costes.md](teoria/03-optimizacion-costes.md) | [03_cache_semantico.py](labs/03_cache_semantico.py), [04_model_routing.py](labs/04_model_routing.py) | 8 |
| 4 | Docker para LLMs | [04-docker-para-llms.md](teoria/04-docker-para-llms.md) | [docker/](docker/README.md) | 6 |
| 5 | Despliegue open-source | [05-despliegue-open-source.md](teoria/05-despliegue-open-source.md) | [06_ollama_local.py](labs/06_ollama_local.py) | 6 |
| 6 | AWS: despliegue y monitorización | [06-aws-despliegue.md](teoria/06-aws-despliegue.md) | walkthroughs en teoría (sin cuenta AWS) | 6 |
| 7 | Responsible AI | [07-responsible-ai.md](teoria/07-responsible-ai.md) | ejercicios 8–9 | 5 |
| 8 | Seguridad y governance | [08-seguridad-y-governance.md](teoria/08-seguridad-y-governance.md) | [07_prompt_injection.py](labs/07_prompt_injection.py) | 6 |
| 9 | Safety en producción | [09-safety-en-produccion.md](teoria/09-safety-en-produccion.md) | ejercicios 10–12 | 3 |
| — | Ejercicios y repaso | [ejercicios.md](ejercicios.md) | Tests y rúbrica | — |

El orden importa: la observabilidad va primero porque todo lo demás (evaluación, costes,
despliegue) se apoya en poder medir. Seguridad y safety van al final porque presuponen que
ya sabes cómo se despliega y se monitoriza lo que vas a proteger.

## Cómo ejecutar los labs

```bash
# Desde la raíz del repo, con el venv activado
python modulo-05-llmops/labs/01_trazas_manuales.py
python modulo-05-llmops/labs/05_eval_regresion.py; echo "exit code: $?"
```

Cada lab es autocontenido, usa el tier actual de volumen (`gpt-5.6-luna`, catálogo de
agosto de 2026) y explica en su docstring
qué demuestra y qué deberías observar en la salida.

## Relación con las certificaciones

- **AWS AIF-C01**: los bloques 6, 7, 8 y 9 cubren directamente los dominios de despliegue,
  Responsible AI, seguridad y governance del examen. Material adicional en
  [`certificaciones/aws-aif-c01/`](../certificaciones/aws-aif-c01/).
- **NVIDIA NCA-GENL**: el bloque 5 (vLLM, Triton) cubre el dominio de serving e inferencia.
