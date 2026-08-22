# 01 — Técnicas base: zero-shot, few-shot, chain-of-thought y self-consistency

> Lab asociado: [`../labs/01_zero_vs_few_shot.py`](../labs/01_zero_vs_few_shot.py) y [`../labs/02_chain_of_thought.py`](../labs/02_chain_of_thought.py)

## Por qué existen "técnicas" de prompting

Un LLM autoregresivo genera el siguiente token condicionado a todo lo anterior. El prompt no es una "pregunta" que el modelo "entiende": es el **contexto que condiciona la distribución de probabilidad** de la salida. Las técnicas de prompting son, en el fondo, formas sistemáticas de mover esa distribución hacia donde nos interesa:

- **Zero-shot**: confiar en lo que el modelo aprendió en preentrenamiento e instruction tuning.
- **Few-shot (in-context learning)**: condicionar con ejemplos dentro del propio prompt.
- **Chain-of-thought (CoT)**: hacer que el modelo genere pasos intermedios antes de la respuesta, porque esos tokens intermedios condicionan (y mejoran) la respuesta final.
- **Self-consistency**: muestrear varias cadenas de razonamiento y quedarse con la respuesta mayoritaria.

La observación clave del in-context learning (Brown et al., 2020, el paper de GPT-3) es que un modelo suficientemente grande puede "aprender" una tarea nueva **sin actualizar pesos**, solo viendo ejemplos en el contexto. Todo este tema es consecuencia de esa propiedad.

---

## 1. Zero-shot

Pedir la tarea directamente, sin ejemplos.

```text
Clasifica el siguiente ticket de soporte en una de estas categorías:
facturacion, tecnico, cuenta, ventas.

Ticket: "No consigo restablecer mi contraseña, el email de recuperación no llega."

Responde solo con la categoría.
```

**Cuándo usarlo:**

- Tareas comunes que el modelo ha visto masivamente en entrenamiento: resumen, traducción, clasificación de sentimiento, extracción sencilla.
- Cuando el coste por token importa (los ejemplos few-shot se pagan en **cada** llamada).
- Como **línea base**: nunca optimices un prompt sin haber medido primero el zero-shot.

**Cuándo NO:**

- Cuando el formato de salida es idiosincrático (tu taxonomía interna de etiquetas, un JSON con campos concretos): el modelo no puede adivinar tus convenciones.
- Tareas con criterio ambiguo donde los ejemplos definen la frontera ("¿un ticket que pide factura y reporta un bug es `facturacion` o `tecnico`?").
- Dominios con jerga propia de tu empresa o cliente.

### Zero-shot bien escrito vs mal escrito

| ❌ Mal | ✅ Bien |
|---|---|
| `¿De qué trata este ticket? "No me llega el email..."` | Instrucción explícita + taxonomía cerrada + formato de salida (ejemplo de arriba) |
| Deja abierta la forma de la respuesta: el modelo puede devolver una frase, una lista o una disculpa | Restringe: "Responde solo con la categoría" |

La mayoría de los "fallos de zero-shot" que se ven en la práctica no son límites del modelo: son instrucciones infra-especificadas. Antes de saltar a few-shot, comprueba que tu zero-shot define **tarea, restricciones y formato de salida**.

---

## 2. Few-shot (in-context learning)

Incluir K ejemplos resueltos antes del caso real.

```text
Clasifica tickets de soporte en: facturacion, tecnico, cuenta, ventas.

Ticket: "Me habéis cobrado dos veces la cuota de julio."
Categoría: facturacion

Ticket: "La app se cierra al abrir la pestaña de informes."
Categoría: tecnico

Ticket: "Quiero cambiar el email asociado a mi usuario."
Categoría: cuenta

Ticket: "¿Tenéis descuento para equipos de más de 50 personas?"
Categoría: ventas

Ticket: "No consigo restablecer mi contraseña, el email de recuperación no llega."
Categoría:
```

**Qué aportan realmente los ejemplos.** La investigación sobre in-context learning (p. ej. Min et al., 2022, *Rethinking the Role of Demonstrations*) muestra que gran parte del beneficio viene de que los ejemplos enseñan **el formato, el espacio de etiquetas y la distribución del input**, más que "conocimiento" nuevo. Consecuencia práctica: ejemplos con formato impecable y etiquetas bien balanceadas importan más que tener muchos ejemplos.

**Reglas prácticas:**

1. **3–8 ejemplos** suele ser el punto dulce; más allá, rendimiento marginal decreciente y coste lineal creciente.
2. **Cubre todas las clases** y al menos un caso frontera (el tipo de input que sabes que confunde).
3. **Formato idéntico** entre ejemplos y caso real: mismo delimitador, misma etiqueta, mismas mayúsculas. El modelo imita el patrón literal.
4. **Cuidado con el orden**: los modelos tienen sesgo de recencia (tienden a favorecer la etiqueta de los últimos ejemplos, "recency bias"; Zhao et al., 2021, *Calibrate Before Use*). Mezcla las clases; no pongas todos los `facturacion` juntos.
5. **Ejemplos correctos**: un ejemplo mal etiquetado en el prompt daña más que un 5% de error en un dataset de fine-tuning, porque el modelo lo imita directamente.

**Cuándo NO usar few-shot:**

- Tareas de razonamiento largo: los ejemplos ocupan contexto y no enseñan a razonar (para eso, CoT).
- Cuando los ejemplos pueden **anclar** en exceso: en generación creativa, el modelo clona el estilo de los ejemplos.
- Con structured outputs estrictos (tema 04): si el esquema ya fuerza el formato, los ejemplos de formato sobran; guarda el presupuesto de tokens.
- Datos sensibles: los ejemplos van en cada request; no pongas PII real de clientes como ejemplo.

---

## 3. Chain-of-thought (CoT)

Hacer que el modelo genere razonamiento intermedio antes de la respuesta. Formalizado por **Wei et al., 2022** (*Chain-of-Thought Prompting Elicits Reasoning in Large Language Models*): añadir cadenas de razonamiento a los ejemplos few-shot mejora sustancialmente tareas aritméticas, de sentido común y simbólicas — y el efecto **emerge con la escala** del modelo (en modelos pequeños puede incluso empeorar).

Dos variantes:

### CoT few-shot (la del paper de Wei)

Los ejemplos incluyen el razonamiento:

```text
P: Roger tiene 5 pelotas de tenis. Compra 2 botes con 3 pelotas cada uno.
   ¿Cuántas pelotas tiene ahora?
R: Roger empezó con 5 pelotas. 2 botes de 3 pelotas son 6 pelotas.
   5 + 6 = 11. La respuesta es 11.

P: <caso real>
R:
```

### CoT zero-shot

Kojima et al., 2022 (*Large Language Models are Zero-Shot Reasoners*) demostraron que basta con añadir una instrucción tipo "pensemos paso a paso" ("Let's think step by step") para obtener gran parte del beneficio sin ejemplos.

```text
<caso real>

Razona paso a paso dentro de <razonamiento>...</razonamiento> y después
escribe la respuesta final dentro de <respuesta>...</respuesta>.
```

Separar razonamiento y respuesta con etiquetas (o pedir la respuesta final en la última línea) es esencial en producción: te permite **parsear la respuesta sin regex frágiles** y descartar el razonamiento.

**Cuándo usar CoT:**

- Aritmética, lógica, planificación en varios pasos, análisis de casos con condiciones (contratos, políticas, reglas de negocio).
- Cuando quieres poder **auditar** por qué el modelo respondió lo que respondió.

**Cuándo NO:**

- Tareas de recuperación directa o clasificación trivial: añade latencia y coste sin mejorar (y a veces el modelo "sobre-razona" y se convence de un error).
- Cuando necesitas latencia mínima: CoT multiplica los tokens de salida, que son los caros.
- **Con modelos de razonamiento nativo** (GPT-5.6 con esfuerzo configurable y extended
  thinking de Claude): ya generan razonamiento interno; pedirles que revelen una cadena
  privada es innecesario y frágil. Pide una respuesta verificable, evidencias y checks
  breves. Para volumen, evalúa `gpt-5.6-luna` y `claude-haiku-4-5` contra tus casos.

**Error común:** pedir CoT y a la vez "responde solo con la categoría". Son instrucciones contradictorias; el modelo obedecerá una u otra de forma inestable. Si quieres ambos, pide razonamiento en una sección y respuesta en otra, y parsea la sección de respuesta.

**Advertencia de honestidad del razonamiento:** la cadena generada es una *verbalización*, no una traza fiel del cómputo interno. Hay evidencia (p. ej. Turpin et al., 2023, *Language Models Don't Always Say What They Think*) de que los modelos pueden dar razonamientos plausibles que no reflejan la causa real de su respuesta. Útil para mejorar accuracy y para revisión humana; no lo trates como prueba formal.

---

## 4. Self-consistency

**Wang et al., 2022** (*Self-Consistency Improves Chain of Thought Reasoning in Language Models*): en lugar de una sola cadena de razonamiento con decodificación greedy, se muestrean **N cadenas con temperatura > 0** y se elige la respuesta final **por voto mayoritario**. La intuición: hay muchos caminos de razonamiento válidos hacia la respuesta correcta, pero los errores tienden a dispersarse en respuestas distintas.

```
                     ┌─ cadena 1 → "11"
prompt CoT ── T=0.8 ─┼─ cadena 2 → "11"     → mayoría: "11"
                     ├─ cadena 3 → "12"
                     └─ cadena 4 → "11"
```

Implementación mínima (el lab 02 la construye completa):

```python
from collections import Counter

answers = []
for _ in range(5):
    response = call_llm(cot_prompt, temperature=0.8)
    answers.append(extract_final_answer(response))
majority = Counter(answers).most_common(1)[0][0]
```

**Decisiones de diseño:**

- **N entre 5 y 20** en el paper original; en la práctica N=5 ya captura buena parte de la mejora. El coste escala linealmente con N: self-consistency es la técnica más cara de este tema.
- Necesitas una **respuesta final parseable** (número, etiqueta, opción) para poder votar. En generación libre no hay "mayoría" trivial — ahí la alternativa es generar N candidatos y elegir con un juez (tema 05).
- Temperatura entre 0.5 y 1.0: con temperatura 0 todas las cadenas son casi idénticas y el voto no aporta.

**Cuándo usarla:** decisiones puntuales de alto valor donde el error es caro (clasificación de riesgo, extracción crítica, puertas de un agente). **Cuándo NO:** endpoints de alto volumen — multiplicar el coste ×5–10 por request rara vez se justifica; primero agota prompt + modelo mejor.

---

## Cómo decidir: árbol práctico

```
¿La tarea es común y el formato simple?
 └─ Sí → zero-shot bien especificado. Mide. ¿Suficiente? Fin.
     └─ No suficiente →
        ¿El fallo es de formato/criterio de etiquetado?
         └─ Sí → few-shot (3-8 ejemplos, casos frontera incluidos)
        ¿El fallo es de razonamiento en varios pasos?
         └─ Sí → CoT (zero-shot primero; few-shot CoT si persiste)
            ¿Sigue fallando y el caso justifica ×N de coste?
             └─ Sí → self-consistency (N=5)
                ¿Sigue fallando?
                 └─ Modelo más capaz, descomponer la tarea, o fine-tuning
```

Dos reglas transversales:

1. **Mide cada escalón.** Sin dataset de test (tema 05) este árbol es astrología. La diferencia entre "me parece que few-shot va mejor" y "few-shot sube accuracy de 0.78 a 0.91 en mi dataset" es la diferencia entre opinar e ingeniar.
2. **Las técnicas se componen.** Few-shot + CoT + self-consistency es exactamente la receta del paper de Wang. Pero cada capa añade coste: añade capas solo cuando la métrica lo justifique.

## Errores comunes del tema

1. **Saltar a la técnica antes de especificar la tarea.** El 80% de las mejoras vienen de aclarar instrucción, taxonomía y formato.
2. **Few-shot con ejemplos desbalanceados** → el modelo sobre-predice la clase más representada.
3. **CoT sin separar la respuesta final** → parsing frágil en producción.
4. **Comparar técnicas con una sola ejecución y temperatura > 0** → estás midiendo ruido de muestreo, no la técnica.
5. **Copiar prompts de otro modelo sin re-evaluar** → las técnicas interactúan con el
   modelo concreto; un prompt afinado para una familia o snapshot no es automáticamente
   óptimo en Claude ni en la siguiente versión del mismo proveedor.

## Para profundizar

- Wei, J. et al. (2022). *Chain-of-Thought Prompting Elicits Reasoning in Large Language Models*. arXiv:2201.11903.
- Wang, X. et al. (2022). *Self-Consistency Improves Chain of Thought Reasoning in Language Models*. arXiv:2203.11171.
- Kojima, T. et al. (2022). *Large Language Models are Zero-Shot Reasoners*. arXiv:2205.11916.
- Brown, T. et al. (2020). *Language Models are Few-Shot Learners* (GPT-3). arXiv:2005.14165.
- Min, S. et al. (2022). *Rethinking the Role of Demonstrations*. arXiv:2202.12837.
- Zhao, Z. et al. (2021). *Calibrate Before Use: Improving Few-Shot Performance of Language Models*. arXiv:2102.09690.
- Guía oficial de prompting de Anthropic: https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview
- Guía oficial de prompting de OpenAI: https://platform.openai.com/docs/guides/prompt-engineering
- The Prompt Report (Schulhoff et al., 2024, taxonomía de 58 técnicas): arXiv:2406.06608.
