# Ejercicios — Módulo III

Resuelve primero con el corpus de NebulaOps y conserva configuración, resultados por caso y
conclusiones. Una mejora visual en una consulta no cuenta como evidencia de mejora global.

## 1. Anatomía de un fallo

Elige cinco respuestas incorrectas de un pipeline RAG. Para cada una separa: cobertura del corpus,
ingesta, chunking, retrieval, orden, contexto entregado, generación y cita. Propón una prueba que
pueda falsar tu diagnóstico antes de modificar el sistema.

## 2. Embeddings frente a TF-IDF

Ejecuta los labs 01 y 03 con TF-IDF y con el embedding multilingüe. Compara doc recall@4 y MRR@4
por tag del dataset. Añade seis paráfrasis sin vocabulario compartido y explica dónde gana cada
método. Registra modelo, versión y tiempo de indexación.

## 3. Chunking basado en evidencia

Añade una estrategia recursiva de 100–160 palabras que respete párrafos. Evalúa al menos cuatro
combinaciones de tamaño/overlap. Reporta número de chunks, p50/p95 de longitud, recall, MRR y tres
fallos concretos. Elige una configuración con un criterio declarado antes del experimento.

## 4. Relevancia a nivel de chunk

Amplía `eval_dataset.json` con `relevant_chunk_ids` para diez preguntas. Calcula precision@k,
recall@k, MRR y nDCG. Contrasta esos resultados con el recall por documento y documenta dos casos
en que el documento correcto no contiene la evidencia en el chunk recuperado.

## 5. Reranker en dos etapas

Compara `candidate_k` 5, 10 y 20 con `final_k` 3 y 5. Mide calidad y latencia p50/p95. Incluye un
baseline sin reranking y otro con la heurística offline. Decide si el cross-encoder compensa y para
qué tipo de consulta.

## 6. Retrieval híbrido

Combina ranking lexical y semántico mediante Reciprocal Rank Fusion. No sumes scores crudos de
escalas distintas. Ajusta el parámetro `k` de RRF en desarrollo y congélalo antes del test final.
Analiza consultas con identificadores, cifras, paráfrasis y negaciones.

## 7. Multi-query y HyDE

Construye 12 consultas difíciles y compara baseline, multi-query, HyDE y ambos. Guarda las
expansiones. Marca cualquier afirmación inventada por HyDE y comprueba si desplazó la fuente
correcta. Añade un presupuesto de consultas y una regla para no expandir preguntas sencillas.

## 8. Abstención calibrada

Usa los casos `answerable=false` para calibrar una regla de abstención. Evalúa precisión/recall de
la detección y coste de falsos positivos/falsos negativos. No uses solo el score del vecino sin
normalizar: combina señales de retrieval, cobertura y una respuesta explícita de insuficiencia.

## 9. Citas verificables

Exige una cita por afirmación. Implementa un verificador que compruebe: ID recuperado, cita
existente, fragmento accesible y soporte lexical mínimo. Crea ataques donde el contexto contiene
instrucciones y donde la respuesta cita una fuente real para una afirmación no soportada.

## 10. Evaluación con RAGAS

Ejecuta el lab 06 sobre diez casos con dos configuraciones. Repite el juicio tres veces, calcula
media y rango, y revisa manualmente los cinco peores. Estima llamadas y coste antes de ejecutar.
Explica qué proxies offline correlacionan —o no— con las métricas de juez.

## 11. Ingesta incremental

Diseña IDs estables y un manifest con hash de documento, versión de parser, chunker y embedding.
Implementa alta, modificación y baja sin reindexar todo. Prueba una actualización que elimina una
política obsoleta y demuestra que ya no aparece en retrieval.

## 12. Proyecto — asistente RAG evaluado

Completa la aplicación de `proyecto/` con una interfaz de chat, historial por sesión y panel de
evidencias. Debe permitir comparar dos configuraciones sin cambiar el dataset final.

Entregables mínimos:

```text
rag-nebulaops/
├── corpus-manifest.json
├── app/                    # API y UI
├── eval/                   # dataset, runner, gates y resultados
├── tests/                  # parsing, retrieval, citas y API sin red
├── docs/architecture.md    # ADRs y modelo de amenazas
└── README.md               # ejecución, límites, coste y decisión
```

Gates:

- doc recall@4 ≥ 0,90 y MRR@4 ≥ 0,85 sobre el test congelado;
- cero respuestas con afirmaciones sin una cita recuperada en los casos auditados;
- abstención correcta en al menos 4 de los 5 casos fuera de corpus;
- latencia p95 y coste por consulta medidos con un presupuesto explícito;
- tests offline reproducibles y ningún secreto en artefactos;
- análisis escrito de cinco fallos, incluido al menos uno que las métricas agregadas oculten.

El proyecto se aprueba por la trazabilidad de la decisión, no por alcanzar una cifra aislada.
