# Módulo I — Fundamentos de LLMs y APIs (0,5 ECTS)

> Tiempo estimado: **15–18 horas** (semanas 1–2 del programa).
> Hito de salida: un **cliente multi-proveedor** capaz de invocar OpenAI, Anthropic y
> Amazon Bedrock detrás de una interfaz propia, registrando tokens, latencia y motivo de parada.

Este módulo construye el vocabulario técnico que usarás durante todo el programa. No pretende
que entrenes un transformer desde cero: pretende que entiendas qué ocurre entre el texto de
entrada y el siguiente token, que puedas anticipar el efecto de la tokenización y los parámetros
de muestreo, y que sepas integrar tres APIs sin ocultar sus diferencias importantes.

## Objetivos de aprendizaje

Al terminar deberías ser capaz de:

1. Explicar la arquitectura decoder-only, self-attention, máscara causal, KV cache y el coste
   del contexto sin recurrir a analogías incorrectas.
2. Tokenizar texto, medir diferencias entre idiomas y estimar el impacto sobre contexto y coste.
3. Elegir `temperature`, `top_p` y límites de salida según la tarea, comprobando siempre el
   motivo de parada.
4. Leer una respuesta de OpenAI y Anthropic, incluyendo contenido tipado y uso de tokens.
5. Invocar un foundation model con la Converse API de Amazon Bedrock sin incrustar credenciales.
6. Encapsular proveedores bajo un contrato propio sin borrar sus metadatos ni sus errores.
7. Elegir familia y tamaño de modelo con una evaluación del caso real, no por un ranking aislado.

## Estructura

```text
modulo-01-fundamentos-llm/
├── README.md
├── teoria/
│   ├── 01-arquitectura-transformer.md
│   ├── 02-tokenizacion.md
│   ├── 03-parametros-generacion.md
│   ├── 04-panoramica-modelos.md
│   └── 05-aws-ia-bedrock.md
├── labs/
│   ├── 01_primer_llamada_openai.py
│   ├── 02_primer_llamada_anthropic.py
│   ├── 03_tokenizacion_comparada.py
│   ├── 04_parametros_generacion.py
│   └── 05_bedrock_inference.py
└── ejercicios.md              ← enunciados y criterios verificables
```

## Orden recomendado

| # | Teoría | Práctica | Horas |
|---|---|---|---:|
| 1 | [Arquitectura transformer](teoria/01-arquitectura-transformer.md) | Ejercicio 1 | 3 |
| 2 | [Tokenización](teoria/02-tokenizacion.md) | [Lab 03](labs/03_tokenizacion_comparada.py) + ejercicios 2–3 | 3 |
| 3 | [Parámetros de generación](teoria/03-parametros-generacion.md) | [Lab 04](labs/04_parametros_generacion.py) + ejercicios 4–5 | 3 |
| 4 | [Panorámica de modelos](teoria/04-panoramica-modelos.md) | [Labs 01–02](labs/) + ejercicios 6–7 | 3 |
| 5 | [AWS IA y Bedrock](teoria/05-aws-ia-bedrock.md) | [Lab 05](labs/05_bedrock_inference.py) + ejercicio 8 | 2 |
| 6 | Integración | Ejercicios 9–10: cliente multi-proveedor | 3+ |

## Preparación y ejecución

Completa primero el [setup general](../setup/README.md). Los labs 03 y los ejercicios de
atención son locales. Los labs 01, 02 y 04 consumen una cantidad pequeña de API. El lab 05
requiere una cuenta AWS con acceso explícito al modelo elegido y puede generar coste.

```bash
uv sync
source .venv/bin/activate
python modulo-01-fundamentos-llm/labs/03_tokenizacion_comparada.py
```

Los nombres de modelo se pueden cambiar mediante `OPENAI_MODEL`, `ANTHROPIC_MODEL` y
`BEDROCK_MODEL_ID`. Los alias de modelos cambian con el tiempo: antes de ejecutar un curso
guardado durante meses, contrasta disponibilidad y precio en la documentación oficial.

## Criterio de superación

- Puedes explicar a otra persona el cálculo de atención de una cabeza y resolver el ejercicio 1.
- Has ejecutado los cinco labs y has provocado al menos un caso de truncado o error controlado.
- El cliente del ejercicio 10 devuelve el mismo tipo de resultado para los tres proveedores,
  conserva la metadata original útil y no contiene claves en el código.
- Puedes justificar, con una mini-evaluación, qué modelo usarías para una tarea concreta.
