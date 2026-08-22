# 02 — Embeddings y bases de datos vectoriales

## Qué es un embedding

Un embedding es la representación de un texto como un vector denso de dimensión fija
(384, 768, 1536, 3072...) tal que **textos semánticamente parecidos quedan cerca en el
espacio vectorial**. Es el fundamento del retrieval denso: convertimos "¿cómo pido
vacaciones?" y "política de días libres" en vectores y comprobamos que su similitud
coseno es alta aunque no compartan ni una palabra.

Los modelos de embeddings para retrieval son **bi-encoders**: codifican query y documento
*por separado*, lo que permite precomputar los vectores de todo el corpus offline y
comparar en milisegundos. (El contraste con cross-encoders, que codifican query+documento
juntos, se ve en el [capítulo 04](04-reranking.md).)

### Medidas de similitud

| Medida | Fórmula (intuición) | Notas |
|---|---|---|
| Coseno | ángulo entre vectores | La estándar; ignora la magnitud |
| Producto escalar (dot) | proyección | Equivale a coseno si los vectores están normalizados a norma 1 |
| Euclídea (L2) | distancia geométrica | Con vectores normalizados, ordena igual que coseno |

Casi todos los modelos modernos entregan (o recomiendan) vectores normalizados, con lo
que las tres ordenan igual. Regla práctica: **normaliza y usa coseno/dot**, y asegúrate
de que la métrica configurada en la colección de la DB coincide con la que el modelo
espera — otro bug silencioso clásico.

### Detalles que importan al elegir/usar un modelo

- **Asimetría query/documento**: algunos modelos (la familia E5, los de Cohere) esperan
  prefijos distintos para query y pasaje (`query: ...` / `passage: ...`) o un parámetro
  `input_type`. Omitirlos degrada el retrieval de forma medible.
- **Ventana máxima**: los modelos de embeddings truncan (p. ej. 256-512 tokens en muchos
  sentence-transformers, 8191 en los de OpenAI). Si tu chunk excede la ventana, el final
  del chunk **no existe** para el índice.
- **Idioma**: para corpus en español, verifica que el modelo sea multilingüe
  (`paraphrase-multilingual-*`, `multilingual-e5`, `text-embedding-3-*`, Cohere
  `embed-multilingual-v3`). `all-MiniLM-L6-v2` está entrenado sobre todo en inglés:
  funciona razonablemente en los labs, pero para producción en español hay opciones
  mejores.
- **Dimensión y Matryoshka**: `text-embedding-3-large` (3072 dims) permite truncar el
  vector a 1024 o 256 dimensiones (Matryoshka Representation Learning) intercambiando
  algo de calidad por memoria/velocidad.
- **Benchmark de referencia**: MTEB (Massive Text Embedding Benchmark) publica un
  leaderboard por tarea e idioma. Úsalo para preseleccionar, pero decide con **tu**
  dataset de evaluación: el ranking de MTEB no siempre se traslada a tu dominio.

### Local vs API

| | Local (sentence-transformers) | API (OpenAI, Cohere, Voyage) |
|---|---|---|
| Coste | 0 €/token (solo cómputo) | Por token; barato pero no cero |
| Privacidad | El texto no sale de tu máquina | El texto viaja al proveedor |
| Calidad | Buena; depende del modelo | Estado del arte multilingüe |
| Ops | Tú gestionas modelo y versión | Cero ops; riesgo de deprecación del modelo |
| Latencia | Baja en batch con GPU; ok en CPU para corpus pequeños | Red + rate limits |

En este módulo los labs usan `all-MiniLM-L6-v2` en local (384 dims, rápido en CPU,
coste cero) con OpenAI `text-embedding-3-small` como opción vía variable de entorno.

## Por qué una base de datos vectorial

Buscar los k vecinos más cercanos de forma exacta (kNN por fuerza bruta) es O(N·d) por
query. Para 10k chunks es instantáneo — **no necesitas infraestructura para eso, un
numpy array basta**. Para millones de vectores con latencias de milisegundos, hace falta
**ANN** (Approximate Nearest Neighbors): índices que sacrifican exactitud marginal
(recall ~0.95-0.99) por órdenes de magnitud de velocidad.

### HNSW en dos párrafos

El índice ANN dominante es **HNSW** (Hierarchical Navigable Small World): un grafo
multicapa donde las capas superiores tienen pocos nodos con enlaces largos (autopistas)
y las inferiores muchos nodos con enlaces cortos (calles). La búsqueda entra por arriba,
navega con voracidad hacia el vecino más cercano y desciende de capa, refinando.

Sus parámetros aparecen en toda vector DB: `M` (enlaces por nodo: más = mejor recall,
más RAM), `ef_construction` (esfuerzo al construir el índice) y `ef_search` (esfuerzo
por query: el dial recall↔latencia que puedes ajustar en caliente). Alternativa: IVF
(clustering + búsqueda en los clusters más cercanos), común en pgvector y FAISS, más
barato en RAM y peor en recall a igual latencia.

### Cuantización

Para corpus grandes, la RAM manda: 1M vectores × 1536 dims × 4 bytes ≈ 6 GB solo en
vectores. Las DBs ofrecen cuantización escalar (float32→int8, ~4× menos memoria) y
binaria (~32× menos, con re-scoring sobre los originales para recuperar precisión).

## Comparativa de vector DBs

| | **Pinecone** | **Weaviate** | **Qdrant** | **pgvector** | **Chroma** |
|---|---|---|---|---|---|
| Modelo | SaaS gestionado (serverless) | OSS + cloud | OSS (Rust) + cloud | Extensión de PostgreSQL | OSS embebida + server |
| Despliegue | Solo cloud | Docker/K8s o SaaS | Docker/K8s o SaaS | Donde corra Postgres (RDS, Supabase...) | `pip install`, in-process |
| Búsqueda híbrida | Sí (sparse+dense) | Sí (BM25+dense) | Sí (sparse+dense, RRF) | Con `tsvector` + SQL manual | No nativa |
| Filtrado por metadatos | Sí | Sí (GraphQL/REST) | Sí, con filtros pre-ANN eficientes | SQL completo (joins!) | Básico |
| Multi-tenancy | Namespaces | Sí | Colecciones/particiones + payload filter | Esquemas/filas SQL | Colecciones |
| Punto fuerte | Cero ops, escala sin pensar | Módulos integrados (vectorización, generative) | Rendimiento, filtros, cuantización fina | Tus datos ya viven ahí; transacciones y joins | Prototipado instantáneo |
| Punto débil | Lock-in, coste a escala, no self-host | Operarlo tú tiene curva | Operarlo tú (menos que Weaviate) | Rendimiento ANN inferior a DBs dedicadas en corpus muy grandes | No pensada para producción grande |

### Cómo decidir (árbol práctico)

1. **¿Prototipo o corpus < ~100k chunks?** → Chroma (o numpy). No sobre-ingenierices.
2. **¿Ya tienes PostgreSQL y tu corpus es pequeño-mediano?** → pgvector. Una pieza menos
   de infraestructura, backups y ACL que ya conoces, y puedes hacer `JOIN` entre
   vectores y datos de negocio. Es la opción más infravalorada.
3. **¿Necesitas rendimiento, filtros ricos y control (self-host)?** → Qdrant.
4. **¿Equipo sin capacidad de ops y presupuesto?** → Pinecone.
5. **¿Quieres que la DB también vectorice y genere (todo-en-uno)?** → Weaviate.

En los labs usamos **Chroma** (cero fricción, embebida) y **Qdrant vía Docker** en el
proyecto, que es lo más parecido a producción self-hosted sin coste.

### Qdrant en 30 segundos

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

## Errores comunes

1. **Montar un cluster de vector DB para 5.000 chunks.** Fuerza bruta con numpy o Chroma
   resuelve el 90 % de los casos de empresa. La infraestructura llega cuando los números
   la piden.
2. **Métrica de distancia mal configurada** (colección en L2 con un modelo que espera
   coseno sin normalizar): funciona "más o menos", que es peor que fallar.
3. **Olvidar los prefijos query/passage** en modelos asimétricos.
4. **Chunks que exceden la ventana del modelo de embeddings**: el índice solo ve el
   principio de cada chunk.
5. **Filtrar después de buscar**: pedir top-10 y filtrar por metadatos en cliente puede
   dejarte con 0 resultados. El filtro va en la query (pre-filtering), y Qdrant lo hace
   bien incluso con filtros muy selectivos.
6. **No guardar el texto y los metadatos junto al vector**: acabas con IDs huérfanos.
7. **Comparar DBs por benchmarks de marketing**: los números publicados por cada vendor
   se miden en condiciones que les favorecen. Si el rendimiento importa, mide con tus
   datos, tu hardware y tus filtros.

## Para profundizar

- Malkov & Yashunin (2016), *Efficient and robust approximate nearest neighbor search
  using HNSW*: https://arxiv.org/abs/1603.09320
- Muennighoff et al. (2022), *MTEB: Massive Text Embedding Benchmark*:
  https://arxiv.org/abs/2210.07316 · Leaderboard: https://huggingface.co/spaces/mteb/leaderboard
- Reimers & Gurevych (2019), *Sentence-BERT* — el origen de sentence-transformers:
  https://arxiv.org/abs/1908.10084
- Documentación de Qdrant (conceptos, cuantización, filtrado):
  https://qdrant.tech/documentation/
- Documentación de pgvector: https://github.com/pgvector/pgvector
