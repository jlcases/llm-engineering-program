# 05 — Evaluación de prompts: datasets de test, LLM-as-judge y A/B testing

> Labs asociados: [`../labs/06_eval_prompts_dataset.py`](../labs/06_eval_prompts_dataset.py) y [`../labs/07_ab_testing_prompts.py`](../labs/07_ab_testing_prompts.py)
> Este es el tema central del módulo: su hito de salida es un pipeline de evaluación funcionando.

## El problema del "a mí me funciona"

El flujo de trabajo por defecto con prompts es: pruebas 3 entradas a mano, la salida "se ve bien", a producción. Eso tiene dos fallos estructurales:

1. **Muestra ridícula y sesgada**: tus 3 entradas de prueba no representan la distribución real (nadie prueba a mano los tickets escritos en mayúsculas, con dos temas mezclados, o en catalán).
2. **Sin memoria**: cuando toques el prompt el mes que viene, no sabrás si mejoraste el caso nuevo *y* rompiste cinco antiguos.

La solución es la misma que el software resolvió hace décadas: **tests**. Un prompt es código; se evalúa con datasets, métricas y regresión. La diferencia con el software clásico es que la salida es estocástica y a veces no hay "respuesta correcta" única — de ahí las tres herramientas de este tema.

## 1. Datasets de test (golden datasets)

Un dataset de evaluación es una lista de casos `{input, resultado_esperado}` (más metadatos). Para la clasificación de tickets del módulo:

```json
{
  "id": "t-014",
  "texto": "ME HABÉIS COBRADO DOS VECES!!! quiero mi dinero YA",
  "categoria_esperada": "facturacion",
  "dificultad": "facil",
  "nota": "tono agresivo, no debe confundir con 'cuenta'"
}
```

**Cómo construirlo:**

- **Empieza con 20–50 casos.** Es suficiente para detectar diferencias grandes entre prompts y cabe en el presupuesto de cualquiera. Crece hacia 200+ con el tiempo.
- **Fuentes por orden de calidad**: (1) datos reales de producción anonimizados, (2) casos de fallo reportados, (3) casos sintéticos generados por un LLM **y revisados a mano** — la revisión no es opcional: el generador comete los mismos errores sistemáticos que luego querrás detectar.
- **Cubre la distribución fea**: casos frontera entre clases, entradas ambiguas, texto mal escrito, entradas vacías o fuera de dominio, intentos de injection. Un dataset de casos bonitos mide poco.
- **Etiqueta con criterio documentado**: si dos personas etiquetarían distinto un caso, escribe la regla de desempate en el propio dataset (campo `nota`). Ese documento de criterio es oro: es lo que luego le darás al LLM-judge.
- **Congélalo y versiónalo** junto al prompt (tema 06). Si cambias casos, cambia la versión: comparar accuracy entre datasets distintos no significa nada.

**Métricas programáticas** (cuando hay respuesta correcta):

| Tarea | Métrica |
|---|---|
| Clasificación | accuracy, y por-clase precision/recall si hay desbalance |
| Extracción | exact match por campo, F1 sobre campos |
| Salida estructurada | % de parseos válidos + métricas por campo |
| Generación con restricciones | checks programáticos: longitud, presencia de secciones, regex |

Ejecuta siempre con `temperature=0` (o la mínima) para evaluar: quieres medir el prompt, no el ruido de muestreo. Si la tarea de producción usa temperatura alta, evalúa con N muestras por caso y promedia.

## 2. LLM-as-judge

Para salidas sin respuesta única (resúmenes, respuestas a clientes, explicaciones) las métricas programáticas no llegan. Las métricas clásicas de NLP (BLEU, ROUGE) correlacionan mal con calidad real. La práctica estándar actual: **usar un LLM como evaluador**, formalizada en Zheng et al., 2023 (*Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena*), que midió que jueces LLM fuertes alcanzan >80% de acuerdo con preferencias humanas — comparable al acuerdo entre humanos.

Tres modos de juicio:

1. **Puntuación con rúbrica** (single answer grading): "puntúa de 1 a 5 según estos criterios". Útil para monitorizar en el tiempo.
2. **Comparación por pares** (pairwise): "¿respuesta A o respuesta B?" Mucho más fiable que la puntuación absoluta (los LLMs puntúan con escalas inconsistentes, pero comparan bien). Es la base del A/B testing de abajo.
3. **Verificación de criterios binarios**: "¿la respuesta menciona el plazo de 14 días? ¿contiene alguna promesa de reembolso?" — el modo más robusto de los tres, porque cada check es casi programático.

### Escribir un buen prompt de juez

El juez es un prompt más, con sus propias reglas:

```text
Eres un evaluador de respuestas de soporte al cliente de un SaaS de
facturación. Evalúa la respuesta según esta rúbrica, criterio a criterio:

<rubrica>
1. Corrección: ¿es exacta según la política de la empresa? (sin inventar
   funcionalidades ni prometer reembolsos)
2. Completitud: ¿responde a todo lo que preguntó el cliente?
3. Tono: ¿profesional, empático, en español correcto?
</rubrica>

<pregunta_cliente>{{question}}</pregunta_cliente>
<respuesta_a_evaluar>{{answer}}</respuesta_a_evaluar>

Analiza cada criterio en <analisis>, después da un veredicto JSON:
{"correccion": 1-5, "completitud": 1-5, "tono": 1-5, "veredicto_global": "aprobado|rechazado"}
```

Reglas del juez:

- **Rúbrica explícita y descompuesta.** "Evalúa la calidad" produce ruido; criterios concretos producen señal. Aprovecha el documento de criterio del dataset.
- **Razonamiento antes del veredicto** (CoT del juez): mejora la fiabilidad y te deja auditar los juicios.
- **Juez ≥ evaluado**: usa un modelo igual o más capaz como juez que el que genera. Juzgar es más fácil que generar, pero un juez débil añade su propio ruido.
- **Salida estructurada del juez** (tema 04): el veredicto tiene que ser parseable para agregarlo.

### Sesgos conocidos del juez (y mitigaciones)

Documentados en el propio paper de Zheng et al.:

| Sesgo | Qué pasa | Mitigación |
|---|---|---|
| Posición | En pairwise, favorece sistemáticamente la primera (o segunda) opción | Evalúa cada par **dos veces con orden invertido**; si los veredictos discrepan, cuenta como empate |
| Verbosidad | Prefiere respuestas más largas a igual contenido | Rúbrica con criterio explícito de concisión; comparar longitudes en el análisis |
| Auto-preferencia | Un modelo tiende a preferir salidas de su propia familia | Juez de familia distinta al generador, o dos jueces |
| Anclaje en la forma | Formato bonito (markdown, listas) infla la nota | Pedir al juez que ignore el formato si no es criterio |

Y la regla meta: **calibra el juez contra humanos una vez.** Etiqueta 20–30 casos a mano, pásale el juez, mide el acuerdo. Si el juez no está de acuerdo contigo en ≥80–90%, arregla el prompt del juez antes de fiarte de sus números.

## 3. A/B testing de prompts

Con dataset + métrica (programática o juez), comparar el prompt A con el B es un experimento:

```
para cada caso del dataset:
    salida_A = llm(prompt_A, caso)
    salida_B = llm(prompt_B, caso)
    veredicto = comparar(salida_A, salida_B)   # métrica o juez pairwise (×2 órdenes)

agregar: % victorias A, % victorias B, % empates
```

**El detalle que casi todo el mundo se salta: ¿la diferencia es real o es ruido?** Con 25 casos, que A gane 14–11 no significa nada. Criterio mínimo sin necesidad de un curso de estadística:

- Usa un **test de signos** o binomial sobre los casos no-empate: si A gana w de n comparaciones decididas, bajo la hipótesis nula (los prompts son iguales) w sigue una Binomial(n, 0.5). Con n=20 decididas, necesitas ~15 victorias (75%) para p<0.05.
- Traducción práctica: con datasets de 20–50 casos **solo detectas diferencias grandes**. Para diferencias finas, amplía dataset antes de sacar conclusiones.
- Reporta siempre los tres números (victorias/derrotas/empates) y algunos ejemplos de casos donde difieren — los ejemplos concretos suelen enseñar más que el porcentaje.

**A/B offline vs online.** Todo lo anterior es evaluación *offline* (pre-despliegue). El A/B *online* (dividir tráfico real entre dos versiones de prompt y medir métricas de producto: resolución, escalado a humano, satisfacción) es la validación definitiva, pero requiere infraestructura de feature flags y volumen. El flujo maduro: offline para iterar rápido y filtrar, online para confirmar lo que importa.

## El pipeline completo

El mini-proyecto del módulo une las piezas:

```
prompts/ (versionados) ──┐
                         ├─→ runner (ejecuta N×M) ─→ métricas programáticas
dataset de test ─────────┘                        ─→ juez LLM (si aplica)
                                                        │
                              informe: tabla por prompt, comparación,
                              regresiones vs versión anterior, coste de la eval
```

Herramientas existentes que implementan este pipeline (para conocerlas; en los labs lo construimos a mano precisamente para entenderlo): **promptfoo** (config YAML, muy directo para prompts), **Inspect** (framework de evals de AISI, Python), **LangSmith** / **Braintrust** / **Langfuse** (plataformas con datasets, runs y jueces integrados), **OpenAI Evals**. En el módulo 8 se retoma la evaluación como proceso continuo en producción.

## Cuánto cuesta evaluar (y por qué da igual)

50 casos × 2 prompts × (1 generación + 2 juicios) ≈ 300 llamadas a modelos baratos ≈ **céntimos**. Comparado con el coste de desplegar un prompt peor —o de discutir en una reunión sobre cuál "parece mejor"— la evaluación es la parte gratis del trabajo. El coste real es construir el dataset: por eso se versiona y se cuida como un activo.

## Errores comunes

1. **Evaluar sobre los mismos casos con los que iteraste el prompt.** Eso es overfitting manual al "train set". Guarda un subconjunto que no miras durante el desarrollo y úsalo solo para la comparación final.
2. **Cambiar prompt y dataset a la vez** → números incomparables.
3. **Fiarse de una sola pasada del juez en pairwise** sin invertir el orden → el sesgo de posición puede decidir tu A/B.
4. **Promediar todo en un solo número** → un prompt puede subir la media y hundir una clase concreta. Mira por-clase/por-dificultad.
5. **Dataset solo de casos fáciles** → todos los prompts sacan 95% y concluyes que "da igual el prompt".
6. **No registrar modelo, temperatura y versión de prompt en los resultados** → resultados irreproducibles a la semana.
7. **Optimizar la métrica y no el objetivo** (Goodhart): si el juez premia longitud, tus prompts "mejorarán" alargándose.

## Para profundizar

- Zheng, L. et al. (2023). *Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena*. arXiv:2306.05685.
- Anthropic — *Create strong empirical evaluations*: https://docs.anthropic.com/en/docs/build-with-claude/develop-tests
- OpenAI — *Evals* (guía y framework): https://platform.openai.com/docs/guides/evals
- promptfoo: https://www.promptfoo.dev/docs/intro/
- Inspect (UK AISI): https://inspect.aisi.org.uk/
- Hamel Husain — *Your AI Product Needs Evals*: https://hamel.dev/blog/posts/evals/
- Eugene Yan — *Patterns for Building LLM-based Systems* (sección de evals): https://eugeneyan.com/writing/llm-patterns/
