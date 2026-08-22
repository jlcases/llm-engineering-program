# Tokenization: BPE, WordPiece, and Model Comparison

> **Module 1 · Topic 2** · Estimated study time: 2.5 h
> Associated lab: `labs/03_tokenizacion_comparada.py`
> Associated exercises: 2, 3, and 9.

---

## 1. The Problem: Converting Text to Numbers

A Transformer operates on sequences of integers. You must decide how to split the text, and the obvious options fail at opposite extremes:

- **One token per word.** The vocabulary explodes (millions of forms: "eat", "would eat", "eating it"...), any new word or typo becomes an unknown token (`<UNK>`), and agglutinative languages or code are poorly represented.
- **One token per character.** The vocabulary is tiny with no unknown words, but sequences become extremely long (remember: attention is O(n²)), and the model wastes capacity relearning that "c-a-s-a" forms a unit.

The solution adopted by all modern LLMs is intermediate: **subwords** (*subword tokenization*). Frequent words become a single token; rare ones are split into reusable chunks. "Tokenization" can be `["token", "ización"]`: there are never `<UNK>`, and the vocabulary remains manageable (50K–256K entries).

**Analogy.** It’s like a LEGO set with pieces of varying sizes: there are large prefabricated pieces for common things (a whole door) and small pieces to build anything unusual. The tokenizer chooses, for each text, the minimum number of pieces that reconstruct it exactly.

---

## 2. BPE: Byte-Pair Encoding

It is the dominant algorithm (GPT, Llama, Mistral, and —with variants— almost all others). It originated as a compression algorithm in 1994, and Sennrich et al. adapted it for NMT in 2016. The idea:

1. Start with a minimal vocabulary of symbols (characters, or better, **bytes**).
2. Count in the training corpus which **pair of adjacent symbols** is the most frequent.
3. Merge that pair into a new symbol and add it to the vocabulary (a *merge rule*).
4. Repeat until you reach the desired vocabulary size.

### 2.1 Step-by-Step Example

Toy corpus (word → frequency), with `_` marking word boundaries:

```
s o l _      ×5
s o l a _    ×3
s o l a s _  ×2
```

**Iteration 1.** We count adjacent pairs:

| Pair | Frequency |
|---|---|
| (s, o) | 5+3+2 = 10 |
| (o, l) | 5+3+2 = 10 |
| (l, _) | 5 |
| (l, a) | 3+2 = 5 |
| (a, _) | 3 |
| (a, s) | 2 |
| (s, _) | 2 |

Tie at 10; the first is chosen: **merge (s,o) → "so"**. The corpus becomes `so l _`, `so l a _`, `so l a s _`.

**Iteration 2.** Now (so, l) appears 10 times → **merge → "sol"**. Corpus: `sol _`, `sol a _`, `sol a s _`.

**Iteration 3.** (sol, _) appears 5 times and (sol, a) also 5 → **merge (sol,_) → "sol_"**. The full word "sol" is now a single token.

With just 3 merges, the tokenizer already encodes "sol" in 1 token, "sola" in 3 (`sol a _`), and an unseen word as "solo" in `sol o _`. Merges are applied during inference **in the exact order they were learned** — the vocabulary is, literally, the ordered list of merges.

### 2.2 Byte-level BPE

GPT-2 introduced a key refinement: starting from the **256 bytes** instead of Unicode characters. This way, *any* byte string is tokenizable (emojis, Chinese, binary, typos) without needing `<UNK>` or a prior character list. This is what tiktoken (OpenAI) and the Llama 3 and Mistral tokenizers use.

---

## 3. WordPiece: The BERT Variant

WordPiece (Google, used by BERT and its family) is very similar to BPE with two differences:

1. **Merge criterion.** BPE merges the most *frequent* pair; WordPiece merges the pair that most increases the corpus *likelihood* — approximately, it maximizes `freq(ab) / (freq(a) · freq(b))`. It prefers pairs that appear together *more often than chance would predict*, not just common pairs.
2. **Marking.** WordPiece marks continuation chunks with `##` (`jugando → ["jug", "##ando"]`), whereas GPT-style BPE marks the word start by including the space in the token (`" jugando"` with a leading space).

A third family exists, **Unigram** (used via SentencePiece in T5 or Llama 1/2): instead of building the vocabulary by merging from the bottom up, it starts with a massive vocabulary and prunes tokens that contribute least to a probabilistic model. In practice, to consume APIs you only need to know they exist and that **each model has its own tokenizer and they are not interchangeable**.

---

## 4. Model Comparison (2026)

| Model / family | Algorithm | Vocabulary | Note |
|---|---|---|---|
| GPT-3.5 / GPT-4 | byte-level BPE (`cl100k_base`) | ~100K | The "classic" tiktoken encoding |
| GPT-4o / o-series | byte-level BPE (`o200k_base`) | ~200K | Much more efficient for non-English |
| Claude (Anthropic) | Proprietary BPE | not public | Counted via the API (`count_tokens`) |
| Llama 3.x | byte-level BPE (tiktoken base) | 128K | Llama 2 used a 32K SentencePiece tokenizer |
| Mistral | BPE (tekken, tiktoken base) | ~131K in v3 | Publishes `mistral-common` |
| Gemini | SentencePiece | ~256K | Very large, multilingual vocabulary |
| BERT | WordPiece | ~30K | Encoder-only, for contrast |

The important part is not memorizing the table (it expires), but the implications:

- **The same text yields a different token count across models.** Do not compare context limits or prices without accounting for this.
- **Larger vocabularies compress more** (fewer tokens per sentence), especially in languages other than English. The jump from `cl100k` to `o200k` notably reduced the tokens required for Spanish, and even more so for non-Latin languages.
- **tiktoken does not tokenize Claude or Gemini.** It serves as an *estimate*, but for exact figures use the provider's tool (Anthropic provides an endpoint `count_tokens`).

In lab `03_tokenizacion_comparada.py` you will measure this empirically with tiktoken.

---

## 5. Why This Matters to You (Cost, Limits, and Bugs)

### 5.1 Cost and Limits

APIs charge **per token** (input and output, at different rates) and limit context **in tokens**. Mental rule for English: 1 token ≈ 4 characters ≈ 0.75 words. In Spanish, the ratio is worse (more tokens per word) because tokenizer training corpora are English-biased. Translating the same prompt can cost 20–50% more in tokens depending on the model and encoding — measure it, don't assume it (exercise 2). For exact pricing, always check each provider's official pricing page; they change frequently.

### 5.2 Quirks That Explain Famous "Bugs"

- **"How many r's are in strawberry?"** The model doesn't see letters: it sees 1–3 opaque tokens. Counting characters requires spelling it out first (converting each letter into a token).
- **Arithmetic.** "12345" can be tokenized as `123|45`. Modern tokenizers force groups of 1–3 digits precisely so numbers remain manageable.
- **Spaces and capitalization matter.** `"hola"`, `" hola"`, and `"Hola"` are distinct tokens. This is why a prompt ending in a space can degrade the first generated word: you break the natural segmentation.
- **Underrepresented languages** pay a double penalty: more tokens (higher cost and less useful context) and poorer learned representation per token.
- **Code.** Modern tokenizers include tokens for multi-space indentation; this is why current models handle Python much better than GPT-3.

### 5.3 Special Tokens

Chats are not plain text: the conversation is serialized with **special control tokens** (`<|im_start|>`, `<|eot_id|>`, etc.) that delimit system/user/assistant roles according to each model's *chat template*. APIs handle them for you, but they explain why a conversation's token count is slightly higher than the sum of its texts, and why injecting those literals into a prompt is a classic attack vector (providers filter them).

---

## 6. tiktoken in 30 Seconds

```python
import tiktoken

enc = tiktoken.get_encoding("o200k_base")        # tokenizador de GPT-4o
# para un modelo concreto, consulta primero si tiktoken ya reconoce su alias actual

ids = enc.encode("El murciélago hipotecario")     # [4224, 2201, 87390, ...]
print(len(ids))                                   # nº de tokens
print([enc.decode([t]) for t in ids])             # ver cada trozo
```

Two operations: `encode` (text → list of integers) and `decode` (integers → text). Everything else is counting and comparing. Lab 03 uses this to build a complete comparison between `cl100k_base` and `o200k_base` on Spanish, English, and code texts.

---

## 7. Common Mistakes

1. **Counting words instead of tokens** when estimating costs or checking if something fits in the context. Standard deviation of 30–100%.
2. **Using tiktoken for non-OpenAI models** and presenting the result as exact. It is a reasonable approximation, but Claude/Gemini/Llama count differently.
3. **Truncating text by characters** before sending it. You might split a multibyte character or a token in half; truncate by tokens (`enc.decode(ids[:n])`).
4. **Asking the model for character-by-character operations** (counting letters, reversing strings) and concluding it "is dumb". This is a structural limit of tokenization; the solution is to give it a tool (code) or force spelling.
5. **Ending the prompt with a space** or cutting a word in half in few-shot: degrades continuation by breaking the expected segmentation.
6. **Assuming conversation token count = sum of messages.** Chat templates add control tokens per message.

---

## 8. Further Reading

- **Sennrich et al. (2016), *Neural Machine Translation of Rare Words with Subword Units*** — the paper that brought BPE to NLP: https://arxiv.org/abs/1508.07909
- **Andrej Karpathy, *Let's build the GPT Tokenizer*** — building a BPE from scratch: https://www.youtube.com/watch?v=zduSFxRajkE
- **tiktoken (OpenAI)** — code and encodings: https://github.com/openai/tiktoken
- **OpenAI Tokenizer Playground** — for visual experimentation: https://platform.openai.com/tokenizer
- **Hugging Face, NLP course, tokenizers chapter** (BPE vs WordPiece vs Unigram): https://huggingface.co/learn/llm-course/chapter6/1
- **Anthropic, token counting endpoint**: https://docs.anthropic.com/en/docs/build-with-claude/token-counting
