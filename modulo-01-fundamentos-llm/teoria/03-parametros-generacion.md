# Parámetros de generación: temperature, top_p, top_k y penalties

> **Módulo 1 · Tema 3** · Tiempo estimado de estudio: 2,5 h
> Lab asociado: `labs/04_parametros_generacion.py`
> Ejercicios asociados: 4 y 5.

---

## 1. El punto de partida: una distribución de probabilidad

Al final del tema 1 vimos que un LLM, en cada paso de generación, no produce "una
palabra": produce un **logit** (una puntuación real) para *cada token del vocabulario*.
El softmax convierte esos logits en probabilidades:

```
P(token_i) = e^(z_i) / Σ_j e^(z_j)
```

La generación consiste en **muestrear** un token de esa distribución, añadirlo a la
secuencia y repetir. Todos los parámetros de este tema hacen exactamente una cosa:
**modificar la distribución antes de muestrear**. No cambian lo que el modelo "sabe";
cambian cómo de arriesgado es al elegir.

**Analogía.** El modelo es un pianista que en cada nota tiene claro qué opciones encajan
y cómo de bien. Temperature decide cuánto improvisa; top_p y top_k le prohíben las notas
absurdas; las penalties le impiden repetir el mismo riff en bucle.

---

## 2. Temperature: la palanca principal

La temperature `T` divide los logits antes del softmax:

```
P(token_i) = e^(z_i / T) / Σ_j e^(z_j / T)
```

- `T < 1` → agranda las diferencias entre logits → la distribución se **afila**
  (el favorito acapara probabilidad). Salida más determinista y conservadora.
- `T = 1` → distribución tal cual la produce el modelo.
- `T > 1` → aplana la distribución → más masa a tokens improbables. Salida más diversa
  y, pasado un punto, incoherente.
- `T = 0` → caso límite: *greedy decoding*, siempre el token más probable.

### 2.1 Ejemplo numérico

Tres tokens candidatos con logits `gato = 2.0`, `perro = 1.0`, `loro = 0.1`:

| | z/T | e^(z/T) | Probabilidad |
|---|---|---|---|
| **T = 1.0** | 2.0 / 1.0 / 0.1 | 7.39 / 2.72 / 1.11 | **0.66 / 0.24 / 0.10** |
| **T = 0.5** | 4.0 / 2.0 / 0.2 | 54.6 / 7.39 / 1.22 | **0.86 / 0.12 / 0.02** |
| **T = 2.0** | 1.0 / 0.5 / 0.05 | 2.72 / 1.65 / 1.05 | **0.50 / 0.30 / 0.19** |

Con T=0.5, "gato" pasa del 66 % al 86 %; con T=2, "loro" casi duplica sus opciones.
Fíjate en que el **orden nunca cambia** — temperature no reordena candidatos, solo
redistribuye la probabilidad entre ellos.

### 2.2 T = 0 no garantiza determinismo total

Con T=0 el muestreo es greedy, pero en la práctica dos llamadas idénticas pueden diferir
ligeramente: hay no-determinismo por batching en el servidor, aritmética en coma flotante
y actualizaciones del modelo detrás del mismo nombre. OpenAI ofrece `seed` como
"mejor esfuerzo" de reproducibilidad. Trátalo como *casi* determinista, nunca como
garantía criptográfica. Lo comprobarás empíricamente en el ejercicio 4.

---

## 3. Truncar la cola: top_k y top_p

El problema de subir la temperature es la **cola larga**: un vocabulario tiene 100K+
tokens, y aunque cada token absurdo tenga probabilidad minúscula, la suma de miles de
absurdos es relevante. Un solo token malo muestreado puede descarrilar todo lo que sigue
(el error se autoalimenta: el modelo continúa coherentemente su propio disparate).

### 3.1 top_k

Quédate solo con los `k` tokens más probables, renormaliza y muestrea entre ellos.
Simple, pero rígido: `k = 40` puede ser demasiado permisivo cuando la distribución está
concentrada ("La capital de Francia es...") y demasiado restrictivo cuando es plana
("Escribe un primer verso...").

### 3.2 top_p (nucleus sampling)

En vez de un número fijo de candidatos, fija una **masa de probabilidad acumulada**:
ordena los tokens de mayor a menor probabilidad y quédate con el conjunto más pequeño que
sume ≥ `p`. Con `top_p = 0.9`:

- Distribución concentrada: `[0.85, 0.10, 0.03, ...]` → sobreviven 2 tokens.
- Distribución plana: `[0.08, 0.07, 0.06, ...]` → sobreviven decenas.

El corte **se adapta a la confianza del modelo** en cada paso; por eso top_p (propuesto
en Holtzman et al. 2019, *The Curious Case of Neural Text Degeneration*) desplazó a top_k
como truncado por defecto. Las APIs de OpenAI y Anthropic exponen `top_p`; `top_k` lo
exponen Anthropic, Bedrock y la mayoría de stacks locales (llama.cpp, vLLM, Ollama).

### 3.3 Orden de aplicación y regla práctica

El pipeline típico es: logits → temperature → top_k → top_p → muestreo. Interactúan
entre sí, y por eso **la recomendación universal (OpenAI la incluye en su documentación)
es ajustar temperature *o* top_p, no ambos a la vez**: mover los dos hace imposible
atribuir los cambios de comportamiento a una causa.

---

## 4. Penalties: combatir la repetición

Los LLM tienen tendencia a los bucles ("muy muy muy...") porque repetir lo ya generado
suele ser localmente probable. Dos mecanismos clásicos (API de OpenAI, rango -2.0 a 2.0):

- **frequency_penalty**: resta a cada logit una cantidad **proporcional al número de
  veces** que ese token ya ha aparecido. Castiga la repetición insistente.
- **presence_penalty**: resta una cantidad **fija** si el token ha aparecido al menos una
  vez. Empuja a introducir temas/vocabulario nuevos, aunque el token solo saliera una vez.

```
logit_final = logit - freq_penalty · count(token) - pres_penalty · [count(token) > 0]
```

Valores negativos hacen lo contrario (fomentan repetir). En la práctica: empieza en 0;
si ves bucles, prueba 0.1-0.5 de frequency_penalty. Valores altos (>1) producen textos
que evitan palabras normales de forma antinatural. La API de Anthropic no expone estas
penalties (los modelos Claude están entrenados para no necesitarlas); los stacks locales
suelen ofrecer además `repetition_penalty` (multiplicativa, estilo HF/vLLM).

---

## 5. Los demás mandos del panel

- **max_tokens**: tope de tokens de *salida*. No es un objetivo ("escribe 500 tokens")
  sino un techo: si se alcanza, la respuesta llega **truncada** — compruébalo siempre
  (`finish_reason == "length"` en OpenAI, `stop_reason == "max_tokens"` en Anthropic).
  En Anthropic el parámetro es obligatorio.
- **stop / stop_sequences**: cadenas que detienen la generación al aparecer. Útiles para
  delimitar formatos (parar en `"\n\n"`, en `"```"`, en `"FIN"`).
- **seed** (OpenAI): intento de reproducibilidad de mejor esfuerzo, combinado con
  `system_fingerprint` para detectar cambios de backend.
- **logprobs**: devuelve las log-probabilidades de los tokens generados (y las
  alternativas top-N). Oro para depurar: te enseña *cómo de seguro* estaba el modelo en
  cada paso. Base de técnicas de detección de alucinación y de clasificación calibrada.
- **n** (OpenAI): número de respuestas alternativas por llamada.

---

## 6. Recetas por caso de uso

No hay valores mágicos, pero sí puntos de partida sensatos:

| Caso de uso | temperature | Otros | Por qué |
|---|---|---|---|
| Extracción de datos, clasificación | 0 - 0.2 | — | Quieres la respuesta modal, reproducible |
| Código | 0 - 0.3 | — | Un token creativo = un bug |
| RAG / respuesta factual | 0 - 0.4 | — | Fidelidad a las fuentes |
| Chat de propósito general | 0.7 - 1.0 | top_p 0.9-1 | Naturalidad sin descarrilar |
| Escritura creativa, brainstorming | 1.0 - 1.3 | top_p 0.95 | Diversidad; genera varias muestras |
| Datos sintéticos variados | 1.0+ | presence_penalty > 0 | Evitar que todas las muestras se parezcan |

Dos matices importantes en 2026:

1. **Los modelos de razonamiento no siempre exponen estos parámetros.** Algunos ignoran
   o rechazan `temperature`/`top_p` salvo en modos concretos; con *extended thinking* de
   Claude, `temperature` debe ir a 1. El muestreo del "pensamiento" lo controla el
   proveedor.
2. **El rango de temperature depende de la API**: OpenAI admite 0-2; Anthropic 0-1.
   Un "0.7" no significa exactamente lo mismo entre proveedores; recalibra al migrar.

---

## 7. Verlo con tus propios ojos

El lab `04_parametros_generacion.py` lanza el mismo prompt con una parrilla de
temperatures (0, 0.4, 0.8, 1.2) y varias muestras por valor, y te muestra lado a lado
la variabilidad. Cosas en las que fijarte al ejecutarlo:

- Con T=0 las muestras son (casi) idénticas.
- La diversidad crece de forma no lineal: de 0.8 a 1.2 hay más salto que de 0 a 0.4.
- La coherencia se mantiene sorprendentemente bien incluso con T alta *si* top_p
  recorta la cola — prueba a subir top_p a 1 con T=1.2 y compara.

---

## 8. Errores comunes

1. **Tocar temperature y top_p a la vez** y no poder explicar qué cambió. Uno cada vez.
2. **T=0 para tareas creativas**: obtienes el tópico más manido posible (la respuesta
   modal es, por definición, la más previsible).
3. **T alta para extracción/JSON**: un solo token improbable rompe el parseo. Para salida
   estructurada: T baja y, mejor, *structured outputs* (módulo 3).
4. **Interpretar max_tokens como longitud objetivo** y no comprobar el motivo de parada.
   Respuestas truncadas en producción casi siempre son esto.
5. **Confiar en T=0 como determinismo absoluto** para tests. Usa aserciones semánticas,
   no igualdad de cadenas.
6. **Copiar valores entre proveedores** sin mirar rangos y defaults (0-2 vs 0-1, top_k
   disponible o no, penalties disponibles o no).
7. **Usar penalties para arreglar bucles que en realidad son un mal prompt** (p. ej.
   pedir "lista exhaustiva" sin criterio de fin).

---

## 9. Para profundizar

- **Holtzman et al. (2019), *The Curious Case of Neural Text Degeneration*** — el paper
  de nucleus sampling (top_p): https://arxiv.org/abs/1904.09751
- **Documentación actual de modelos y parámetros de OpenAI**:
  https://developers.openai.com/api/docs/models
- **Documentación de la API de Anthropic (Messages API)**:
  https://docs.anthropic.com/en/api/messages
- **OpenAI Cookbook, uso de logprobs**:
  https://cookbook.openai.com/examples/using_logprobs
- **Chip Huyen, *Generation configurations: temperature, top-k, top-p, and test time sampling***
  (capítulo de sampling de *AI Engineering*, 2025): https://huyenchip.com/2024/01/16/sampling.html
