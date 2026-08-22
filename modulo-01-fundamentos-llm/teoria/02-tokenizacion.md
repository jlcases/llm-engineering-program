# Tokenización: BPE, WordPiece y comparativa entre modelos

> **Módulo 1 · Tema 2** · Tiempo estimado de estudio: 2,5 h
> Lab asociado: `labs/03_tokenizacion_comparada.py`
> Ejercicios asociados: 2, 3 y 9.

---

## 1. El problema: convertir texto en números

Un Transformer opera sobre secuencias de enteros. Hay que decidir cómo trocear el texto,
y las opciones obvias fallan por extremos opuestos:

- **Un token por palabra.** El vocabulario explota (millones de formas: "comer", "comería",
  "comiéndoselo"...), cualquier palabra nueva o errata es un token desconocido (`<UNK>`),
  y los idiomas aglutinantes o el código quedan fatal representados.
- **Un token por carácter.** Vocabulario diminuto y sin palabras desconocidas, pero las
  secuencias se hacen larguísimas (recuerda: la atención es O(n²)) y el modelo gasta
  capacidad en reaprender que "c-a-s-a" forma una unidad.

La solución adoptada por todos los LLM modernos es intermedia: **subpalabras**
(*subword tokenization*). Las palabras frecuentes son un solo token; las raras se parten
en trozos reutilizables. "Tokenización" puede ser `["token", "ización"]`: nunca hay
`<UNK>` y el vocabulario se mantiene manejable (50K-256K entradas).

**Analogía.** Es como un juego de LEGO con piezas de varios tamaños: hay piezas grandes
prefabricadas para lo común (una puerta entera) y piezas pequeñas para construir
cualquier cosa rara. El tokenizador elige, para cada texto, el menor número de piezas
que lo reconstruyen exactamente.

---

## 2. BPE: Byte-Pair Encoding

Es el algoritmo dominante (GPT, Llama, Mistral y —con variantes— casi todos). Nació como
algoritmo de compresión en 1994 y Sennrich et al. lo adaptaron a NMT en 2016. La idea:

1. Empieza con un vocabulario de símbolos mínimos (caracteres, o mejor, **bytes**).
2. Cuenta en el corpus de entrenamiento qué **par de símbolos adyacentes** es el más
   frecuente.
3. Fusiona ese par en un símbolo nuevo y añádelo al vocabulario (una *merge rule*).
4. Repite hasta alcanzar el tamaño de vocabulario deseado.

### 2.1 Ejemplo paso a paso

Corpus de juguete (palabra → frecuencia), con `_` marcando fin de palabra:

```
s o l _      ×5
s o l a _    ×3
s o l a s _  ×2
```

**Iteración 1.** Contamos pares adyacentes:

| Par | Frecuencia |
|---|---|
| (s, o) | 5+3+2 = 10 |
| (o, l) | 5+3+2 = 10 |
| (l, _) | 5 |
| (l, a) | 3+2 = 5 |
| (a, _) | 3 |
| (a, s) | 2 |
| (s, _) | 2 |

Empate a 10; se toma el primero: **merge (s,o) → "so"**. El corpus queda
`so l _`, `so l a _`, `so l a s _`.

**Iteración 2.** Ahora (so, l) aparece 10 veces → **merge → "sol"**.
Corpus: `sol _`, `sol a _`, `sol a s _`.

**Iteración 3.** (sol, _) aparece 5 veces y (sol, a) también 5 → **merge (sol,_) → "sol_"**.
La palabra completa "sol" ya es un único token.

Con solo 3 merges, el tokenizador ya codifica "sol" en 1 token, "sola" en 3 (`sol a _`)
y una palabra nunca vista como "solo" en `sol o _`. Las merges se aplican en inferencia
**en el mismo orden en que se aprendieron** — el vocabulario es, literalmente, la lista
ordenada de fusiones.

### 2.2 Byte-level BPE

GPT-2 introdujo un refinamiento clave: partir de los **256 bytes** en vez de caracteres
Unicode. Así *cualquier* cadena de bytes es tokenizable (emojis, chino, binario, erratas)
sin necesidad de `<UNK>` ni de una lista previa de caracteres. Es lo que usan tiktoken
(OpenAI) y los tokenizadores de Llama 3 y Mistral.

---

## 3. WordPiece: la variante de BERT

WordPiece (Google, usado por BERT y familia) es muy parecido a BPE con dos diferencias:

1. **Criterio de fusión.** BPE fusiona el par más *frecuente*; WordPiece fusiona el par
   que más aumenta la *verosimilitud* del corpus — aproximadamente, maximiza
   `freq(ab) / (freq(a) · freq(b))`. Prefiere pares que aparecen juntos *más de lo que
   cabría esperar por azar*, no solo pares comunes.
2. **Marcado.** WordPiece marca los trozos de continuación con `##`
   (`jugando → ["jug", "##ando"]`), mientras que los BPE estilo GPT marcan el inicio de
   palabra incluyendo el espacio en el token (`" jugando"` con espacio inicial).

Existe una tercera familia, **Unigram** (usada vía SentencePiece en T5 o Llama 1/2):
en vez de construir el vocabulario fusionando desde abajo, parte de un vocabulario enorme
y va podando los tokens que menos aportan a un modelo probabilístico. En la práctica, para
consumir APIs te basta con saber que existen y que **cada modelo tiene su tokenizador y
no son intercambiables**.

---

## 4. Comparativa entre modelos (2026)

| Modelo / familia | Algoritmo | Vocabulario | Nota |
|---|---|---|---|
| GPT-3.5 / GPT-4 | byte-level BPE (`cl100k_base`) | ~100K | El encoding "clásico" de tiktoken |
| GPT-4o / o-series | byte-level BPE (`o200k_base`) | ~200K | Mucho más eficiente en no-inglés |
| Claude (Anthropic) | BPE propietario | no público | Se cuenta vía la API (`count_tokens`) |
| Llama 3.x | byte-level BPE (base tiktoken) | 128K | Llama 2 usaba SentencePiece de 32K |
| Mistral | BPE (tekken, base tiktoken) | ~131K en v3 | Publican `mistral-common` |
| Gemini | SentencePiece | ~256K | Vocabulario muy grande, multilingüe |
| BERT | WordPiece | ~30K | Encoder-only, para contraste |

Lo importante no es memorizar la tabla (caduca), sino las consecuencias:

- **El mismo texto tiene distinto número de tokens en cada modelo.** No compares límites
  de contexto ni precios sin tener esto en cuenta.
- **Vocabularios más grandes comprimen más** (menos tokens por frase), especialmente en
  idiomas distintos del inglés. El salto de `cl100k` a `o200k` redujo notablemente los
  tokens necesarios para español, y más aún para lenguas no latinas.
- **tiktoken no tokeniza Claude ni Gemini.** Sirve como *estimación*, pero para cifras
  exactas usa la herramienta del proveedor (Anthropic tiene un endpoint `count_tokens`).

En el lab `03_tokenizacion_comparada.py` medirás esto empíricamente con tiktoken.

---

## 5. Por qué esto te importa (dinero, límites y bugs)

### 5.1 Coste y límites

Las APIs cobran **por token** (de entrada y de salida, a precios distintos) y limitan el
contexto **en tokens**. Regla mental para inglés: 1 token ≈ 4 caracteres ≈ 0,75 palabras.
En español la proporción es peor (más tokens por palabra) porque los corpus de
entrenamiento de los tokenizadores están sesgados al inglés. Un mismo prompt traducido
puede costar un 20-50 % más en tokens según el modelo y el encoding — mídelo, no lo
asumas (ejercicio 2). Para precios concretos, consulta siempre la página oficial de
pricing de cada proveedor; cambian a menudo.

### 5.2 Rarezas que explican "bugs" famosos

- **"¿Cuántas erres tiene strawberry?"** El modelo no ve letras: ve 1-3 tokens opacos.
  Contar caracteres exige deletrear primero (con lo que convierte cada letra en un token).
- **Aritmética.** "12345" puede tokenizarse como `123|45`. Los tokenizadores modernos
  fuerzan grupos de 1-3 dígitos justamente para que los números sean manejables.
- **Espacios y mayúsculas importan.** `"hola"`, `" hola"` y `"Hola"` son tokens
  distintos. Por eso un prompt que termina en espacio puede degradar la primera palabra
  generada: rompes la segmentación natural.
- **Idiomas infrarrepresentados** pagan doble castigo: más tokens (más coste y menos
  contexto útil) y peor representación aprendida por token.
- **Código.** Los tokenizadores modernos incluyen tokens para indentaciones de varios
  espacios; por eso los modelos actuales manejan Python mucho mejor que GPT-3.

### 5.3 Tokens especiales

Los chats no son texto plano: la conversación se serializa con **tokens especiales de
control** (`<|im_start|>`, `<|eot_id|>`, etc.) que delimitan roles system/user/assistant
según la *chat template* de cada modelo. Las APIs los gestionan por ti, pero explican por
qué el recuento de tokens de una conversación es algo mayor que la suma de sus textos, y
por qué inyectar esos literales en un prompt es un vector clásico de ataque (los
proveedores los filtran).

---

## 6. tiktoken en 30 segundos

```python
import tiktoken

enc = tiktoken.get_encoding("o200k_base")        # tokenizador de GPT-4o
# para un modelo concreto, consulta primero si tiktoken ya reconoce su alias actual

ids = enc.encode("El murciélago hipotecario")     # [4224, 2201, 87390, ...]
print(len(ids))                                   # nº de tokens
print([enc.decode([t]) for t in ids])             # ver cada trozo
```

Dos operaciones: `encode` (texto → lista de enteros) y `decode` (enteros → texto).
Todo lo demás es contar y comparar. El lab 03 construye con esto una comparativa
completa entre `cl100k_base` y `o200k_base` sobre textos en español, inglés y código.

---

## 7. Errores comunes

1. **Contar palabras en vez de tokens** al estimar costes o comprobar si algo cabe en el
   contexto. Desviación típica del 30-100 %.
2. **Usar tiktoken para modelos que no son de OpenAI** y presentar el resultado como
   exacto. Es una aproximación razonable, pero Claude/Gemini/Llama cuentan distinto.
3. **Truncar texto por caracteres** antes de enviarlo. Puedes partir un carácter
   multibyte o un token por la mitad; trunca por tokens (`enc.decode(ids[:n])`).
4. **Pedir al modelo operaciones carácter a carácter** (contar letras, invertir cadenas)
   y concluir que "es tonto". Es un límite estructural de la tokenización; la solución es
   darle una herramienta (código) o forzar el deletreo.
5. **Terminar el prompt con espacio** o cortar una palabra a medias en few-shot: degrada
   la continuación por romper la segmentación esperada.
6. **Asumir que el recuento de la conversación = suma de mensajes.** Las chat templates
   añaden tokens de control por mensaje.

---

## 8. Para profundizar

- **Sennrich et al. (2016), *Neural Machine Translation of Rare Words with Subword Units*** —
  el paper que trajo BPE al NLP: https://arxiv.org/abs/1508.07909
- **Andrej Karpathy, *Let's build the GPT Tokenizer*** — construir un BPE desde cero:
  https://www.youtube.com/watch?v=zduSFxRajkE
- **tiktoken (OpenAI)** — código y encodings: https://github.com/openai/tiktoken
- **Tokenizer playground de OpenAI** — para jugar visualmente:
  https://platform.openai.com/tokenizer
- **Hugging Face, curso de NLP, capítulo de tokenizers** (BPE vs WordPiece vs Unigram):
  https://huggingface.co/learn/llm-course/chapter6/1
- **Anthropic, endpoint de token counting**:
  https://docs.anthropic.com/en/docs/build-with-claude/token-counting
