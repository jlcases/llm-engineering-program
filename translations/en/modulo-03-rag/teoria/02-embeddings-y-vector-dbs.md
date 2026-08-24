# 02 — Embeddings and Vector Databases

## What is an embedding

An embedding is the representation of text as a dense vector of fixed dimension
(384, 768, 1536, 3072...) such that **semantically similar texts end up close in the
vector space**. It is the foundation of dense retrieval: we convert "how do I request
leave?" and "paid time off policy" into vectors and verify that their cosine similarity
is high even though they share no words.

Embedding models for retrieval are **bi-encoders**: they encode the query and the document
*separately*, which allows precomputing the vectors for the entire corpus offline and
comparing them in milliseconds. (The contrast with cross-encoders, which encode query+document
together, is covered in [chapter 04](04-reranking.md).)

### Similarity Measures

| Measure | Formula (intuition) | Notes |
|---|---|---|
| Cosine | angle between vectors | The standard; ignores magnitude |
| Dot product | projection | Equivalent to cosine if vectors are normalized to unit norm |
| Euclidean (L2) | geometric distance | With normalized vectors, it orders the same as cosine |

Almost all modern models deliver (or recommend) normalized vectors, meaning
all three metrics produce the same ordering. Practical rule: **normalize and use cosine/dot**, and ensure
that the metric configured in the DB collection matches the one the model
expects — another classic silent bug.

### Details that matter when choosing/using a model

- **Query/document asymmetry**: some models (the E5 family, Cohere models) expect
distinct prefixes for query and passage (`query: ...` / `passage: ...`) or a parameter
`input_type`. Omitting them degrades retrieval in a measurable way.
- **Maximum window**: embedding models truncate (e.g., 256-512 tokens in many
sentence-transformers, 8191 in OpenAI models). If your chunk exceeds the window, the end
of the chunk **does not exist** for the index.
- **Language**: for Spanish corpora, verify that the model is multilingual
(`paraphrase-multilingual-*`, `multilingual-e5`, `text-embedding-3-*`, Cohere
`embed-multilingual-v3`). `all-MiniLM-L6-v2` is trained primarily in English:
it works reasonably well in labs, but for Spanish production there are better options.
- **Dimension and Matryoshka**: `text-embedding-3-large` (3072 dims) allows truncating the
vector to 1024 or 256 dimensions (Matryoshka Representation Learning) trading
some quality for memory/speed.
- **Reference Benchmark**: MTEB (Massive Text Embedding Benchmark) publishes a
leaderboard by task and language. Use it for preselection, but decide with **your**
evaluation dataset: the MTEB ranking does not always transfer to your domain.

### Local vs API

| | Local (sentence-transformers) | API (OpenAI, Cohere, Voyage) |
|---|---|---|
| Cost | 0 €/token (compute only) | Per token; cheap but not zero |
| Privacy | Text does not leave your machine | Text travels to the provider |
| Quality | Good; depends on the model | State-of-the-art multilingual |
| Ops | You manage model and version | Zero ops; risk of model deprecation |
| Latency | Low in batch with GPU; ok on CPU for small corpora | Network + rate limits |

In this module, the labs use `all-MiniLM-L6-v2` locally (384 dims, fast on CPU,
cost zero) with OpenAI `text-embedding-3-small` as an option via environment variable.

## Why a vector database

Searching for the k nearest neighbors exactly (brute-force kNN) is O(N·d) per
query. For 10k chunks, it is instantaneous — **you do not need infrastructure for that, a
numpy array is sufficient**. For millions of vectors with millisecond latencies, you need
**ANN** (Approximate Nearest Neighbors): indexes that sacrifice marginal accuracy
(recall ~0.95-0.99) for orders of magnitude in speed.

### HNSW in two paragraphs

The dominant ANN index is **HNSW** (Hierarchical Navigable Small World): a multi-layer
graph where the upper layers have few nodes with long links (highways)
and the lower layers have many nodes with short links (streets). The search enters from the top,
naviagtes greedily towards the nearest neighbor and descends layers, refining.

Its parameters appear in all vector DBs: `M` (links per node: more = better recall,
more RAM), `ef_construction` (effort when building the index) and `ef_search` (effort
per query: the recall↔latency dial you can adjust on the fly). Alternative: IVF
(clustering + search in the closest clusters), common in pgvector and FAISS, cheaper
in RAM and worse in recall at equal latency.

### Quantization

For large corpora, RAM is key: 1M vectors × 1536 dims × 4 bytes ≈ 6 GB just for
vectors. DBs offer scalar quantization (float32→int8, ~4× less memory)
and binary (~32× less, with re-scoring on the originals to recover precision).

## Vector DB comparison

| | **Pinecone** | **Weaviate** | **Qdrant** | **pgvector** | **Chroma** |
|---|---|---|---|---|---|
| Model | Managed SaaS (serverless) | OSS + cloud | OSS (Rust) + cloud | PostgreSQL Extension | Embedded OSS + server |
| Deployment | Cloud only | Docker/K8s or SaaS | Docker/K8s or SaaS | Where Postgres runs (RDS, Supabase...) | `pip install`, in-process |
| Hybrid search | Yes (sparse+dense) | Yes (BM25+dense) | Yes (sparse+dense, RRF) | With `tsvector` + manual SQL | Not native |
| Metadata filtering | Yes | Yes (GraphQL/REST) | Yes, with efficient pre-ANN filters | Full SQL (joins!) | Basic |
| Multi-tenancy | Namespaces | Yes | Collections/partitions + payload filter | SQL schemas/rows | Collections |
| Strength | Zero ops, scale without thinking | Integrated modules (vectorization, generative) | Performance, filters, fine quantization | Your data already lives there; transactions and joins | Instant prototyping |
| Weakness | Lock-in, cost at scale, no self-host | Operating it yourself has a curve | Operating it yourself (less than Weaviate) | ANN performance inferior to dedicated DBs in very large corpora | Not designed for large-scale production |

### How to decide (practical tree)

1. **Prototype or corpus < ~100k chunks?** → NumPy or a minimal local index. Do not
   over-engineer or expose a server you do not need.
2. **Do you already have PostgreSQL and your corpus is small-medium?** → pgvector. One less piece
   of infrastructure, backups and ACLs that you already know, and you can perform `JOIN` between
   vectors and business data. It is the most underrated option.
3. **Do you need performance, rich filters and control (self-host)?** → Qdrant.
4. **Team without ops capacity and budget?** → Pinecone.
5. **Do you want the DB to also vectorize and generate (all-in-one)?** → Weaviate.

The executable labs use **NumPy/TF-IDF** and preserve IDs and provenance without starting a server.
Qdrant remains an optional exercise when you need filters, persistence, and a dedicated API.

> **Security notice · 2026-08-24:** `chromadb` 1.0.0–1.5.9 is affected by
> [GHSA-f4j7-r4q5-qw2c](https://github.com/advisories/GHSA-f4j7-r4q5-qw2c), a critical
> pre-authentication code-injection vulnerability in the server, and the advisory does not yet list
> a patched version. The course therefore does not install Chroma. If a fix is released, revalidate
> the advisory and threat model before adding it again; never expose a lab instance to an untrusted
> network.

### Qdrant in 30 Seconds

```bash
docker run -d --name qdrant -p 6333:6333 -p 6334:6334 \
  -v qdrant_storage:/qdrant/storage qdrant/qdrant
# Dashboard: http://localhost:6333/dashboard
```

```python
from qdrant_client import QdrantClient, models

client = QdrantClient(url="http://localhost:6333")
client.create_collection(
    collection_name="docs_v1",
    vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE),
)
```

## Common Errors

1. **Setting up a vector DB cluster for 5,000 chunks.** Brute force with NumPy
   solves 90% of enterprise cases. Infrastructure arrives when the numbers
   demand it.
2. **Misconfigured distance metric** (L2 collection with a model expecting
   cosine without normalization): it works "more or less," which is worse than failing.
3. **Forgetting query/passage prefixes** in asymmetric models.
4. **Chunks exceeding the embedding model's window**: the index only sees the
   beginning of each chunk.
5. **Filtering after searching**: requesting top-10 and filtering by metadata on the client side can
   leave you with 0 results. The filter must be in the query (pre-filtering), and Qdrant handles
   it well even with highly selective filters.
6. **Not storing text and metadata alongside the vector**: you end up with orphaned IDs.
7. **Comparing DBs based on marketing benchmarks**: the numbers published by each vendor
   are measured under conditions that favor them. If performance matters, measure with your
   data, your hardware, and your filters.

## For Further Reading

- Malkov & Yashunin (2016), *Efficient and robust approximate nearest neighbor search
  using HNSW*: https://arxiv.org/abs/1603.09320
- Muennighoff et al. (2022), *MTEB: Massive Text Embedding Benchmark*:
  https://arxiv.org/abs/2210.07316 · Leaderboard: https://huggingface.co/spaces/mteb/leaderboard
- Reimers & Gurevych (2019), *Sentence-BERT* — the origin of sentence-transformers:
  https://arxiv.org/abs/1908.10084
- Qdrant Documentation (concepts, quantization, filtering):
  https://qdrant.tech/documentation/
- pgvector Documentation: https://github.com/pgvector/pgvector
