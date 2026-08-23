# Módulo 02 — Contexto y contratos de salida

> Esfuerzo orientativo: **38–45 horas**.
> Prueba de trabajo: **pipeline de evaluación de contratos con dataset y comparación A/B** funcionando de principio a fin.

El contexto y la salida forman una interfaz del sistema. Este módulo pasa de «escribir prompts que parecen funcionar» a diseñar **contratos versionados**: instrucciones con autoridad explícita, salidas estructuradas y un sistema de evaluación que demuestre con datos si una versión es mejor que otra.

## Objetivos de aprendizaje

Al terminar el módulo deberías ser capaz de:

1. Elegir con criterio entre zero-shot, few-shot, chain-of-thought y self-consistency según la tarea, y justificar cuándo **no** usar cada técnica.
2. Estructurar prompts de sistema robustos con roles, delimitadores y etiquetas XML, resistentes a entradas hostiles o ambiguas.
3. Implementar function calling / tool use tanto en la API de OpenAI como en la de Anthropic, incluyendo el bucle completo de ejecución de herramientas.
4. Obtener salidas estructuradas y validadas con JSON mode, `response_format`, Pydantic e Instructor, con reintentos automáticos ante validación fallida.
5. Montar un pipeline de evaluación de prompts: dataset de test, métricas programáticas, LLM-as-judge y A/B testing con criterio estadístico básico.
6. Gestionar prompts como artefactos de software: plantillas, versionado, registries y evaluación en CI.
7. Detectar y mitigar sesgos y alucinaciones actuando a nivel de prompt.

## Estructura del módulo

```
modulo-02-prompt-engineering/
├── README.md                  ← estás aquí
├── teoria/                    ← apuntes, un fichero por tema
├── labs/                      ← código ejecutable, un lab por concepto
│   └── data/                  ← datasets pequeños para los labs
└── ejercicios.md              ← 12 ejercicios + mini-proyecto final y rúbrica
```

## Orden de estudio recomendado

Sigue teoría y lab de cada bloque en pareja: lee el tema, ejecuta el lab, modifícalo, y solo entonces pasa al siguiente.

| # | Teoría | Lab asociado | Horas |
|---|---|---|---|
| 1 | [`teoria/01-tecnicas-base.md`](teoria/01-tecnicas-base.md) — zero-shot, few-shot, CoT, self-consistency | [`labs/01_zero_vs_few_shot.py`](labs/01_zero_vs_few_shot.py) · [`labs/02_chain_of_thought.py`](labs/02_chain_of_thought.py) | 6 |
| 2 | [`teoria/02-system-prompts-y-contexto.md`](teoria/02-system-prompts-y-contexto.md) — system prompts, roles, XML, delimitadores | (se aplica en todos los labs siguientes) | 4 |
| 3 | [`teoria/03-function-calling.md`](teoria/03-function-calling.md) — tool use en OpenAI y Anthropic | [`labs/03_function_calling_openai.py`](labs/03_function_calling_openai.py) · [`labs/04_tool_use_anthropic.py`](labs/04_tool_use_anthropic.py) | 7 |
| 4 | [`teoria/04-structured-outputs.md`](teoria/04-structured-outputs.md) — JSON mode, `response_format`, Pydantic, Instructor | [`labs/05_structured_outputs_instructor.py`](labs/05_structured_outputs_instructor.py) | 5 |
| 5 | [`teoria/05-evaluacion-de-prompts.md`](teoria/05-evaluacion-de-prompts.md) — datasets de test, LLM-as-judge, A/B testing | [`labs/06_eval_prompts_dataset.py`](labs/06_eval_prompts_dataset.py) · [`labs/07_ab_testing_prompts.py`](labs/07_ab_testing_prompts.py) | 8 |
| 6 | [`teoria/06-versionado-y-gestion.md`](teoria/06-versionado-y-gestion.md) — plantillas, registries, prompts en CI | (ejercicios 9–10) | 4 |
| 7 | [`teoria/07-sesgos-y-alucinaciones.md`](teoria/07-sesgos-y-alucinaciones.md) — detección y mitigación a nivel de prompt | (ejercicios 11–12) | 4 |
| 8 | [`ejercicios.md`](ejercicios.md) — mini-proyecto final: pipeline de evaluación propio | — | 2+ |

Las horas incluyen lectura, ejecución y modificación de los labs. El mini-proyecto final puede crecer todo lo que quieras: es el hito del módulo.

## Antes de empezar

1. Entorno preparado según [`../setup/README.md`](../setup/README.md) (`uv sync` + `.env` en la raíz del repo).
2. Necesitas `OPENAI_API_KEY` y `ANTHROPIC_API_KEY` solo para los modos live. Los valores
   de desarrollo verificados en agosto de 2026 son `gpt-5.6-luna` y
   `claude-haiku-4-5`; puedes sobrescribirlos en `.env`. Estima el coste con la tarifa
   oficial vigente antes de ejecutar evaluaciones grandes.
3. Los labs se ejecutan desde la raíz del repo o desde este directorio, da igual: cargan el `.env` de la raíz por ruta absoluta.

```bash
source .venv/bin/activate
python modulo-02-prompt-engineering/labs/01_zero_vs_few_shot.py
```

## Relación con las certificaciones

- **AWS AIF-C01** — dominio 3 (Applications of Foundation Models) pregunta directamente por técnicas de prompting, y el dominio 4 por mitigación de sesgos y alucinaciones.
- **NVIDIA NCA-GENL** — el dominio de "Prompt Engineering" cubre zero/few-shot, CoT y formato de salida.

Cuando termines el módulo, haz las flashcards correspondientes en [`../certificaciones/`](../certificaciones/).
