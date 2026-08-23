# Plantilla de ADR (Architecture Decision Record)

Un ADR captura **una** decisión de arquitectura en el momento en que se toma: qué se decidió, entre
qué opciones y por qué. Su valor aparece después, cuando una persona revisora —o tú mismo— pregunta
"¿por qué no usasteis X?" y la respuesta conserva la información disponible entonces.

Reglas para el proyecto de campo:

- **Numeración secuencial** (`ADR-001`, `ADR-002`…) en `02-documento-de-arquitectura/adr/`, un
  fichero por decisión. Los ADRs no se editan una vez aceptados: si la decisión cambia, se escribe
  uno nuevo que **reemplaza** al anterior y el viejo pasa a estado `reemplazado por ADR-NNN`. Ese
  rastro permite auditar cómo evolucionó el sistema.
- **Mínimo 2 alternativas reales** además de la elegida. "Alternativa: no hacerlo" no cuenta. Si no hubo alternativas serias, no era una decisión de arquitectura.
- **Consecuencias negativas obligatorias.** Toda elección compra algo pagando algo. Un ADR sin contras es marketing.
- Extensión sana: media página a una página. Si pasa de dos, estás documentando implementación, no decisión.

## Formato

```markdown
# ADR-NNN: [decisión en una frase con verbo: "Usar X para Y"]

**Estado:** propuesto | aceptado | reemplazado por ADR-NNN
**Fecha:** AAAA-MM-DD
**Decisores:** [tú; en un equipo real, quiénes]

## Contexto
Qué problema fuerza la decisión y qué restricciones aplican
(presupuesto, plazo, requisitos RNF concretos). 2-4 frases.

## Opciones consideradas
1. Opción A — pros / contras (con números cuando existan)
2. Opción B — pros / contras
3. Opción C — pros / contras

## Decisión
Qué opción se elige y el criterio dominante que inclinó la balanza.

## Consecuencias
- Positivas: …
- Negativas / deuda asumida: …
- Qué señal nos haría revisar esta decisión.
```

---

## Ejemplo relleno

# ADR-003: Usar Qdrant gestionado (free tier) como vector DB en lugar de pgvector o FAISS

**Estado:** aceptado
**Fecha:** 2026-08-24
**Decisores:** J. Cases

## Contexto

El pipeline RAG indexa ~14.000 chunks (corpus CTE, ~19 M de tokens) y debe servir retrieval con filtrado por metadatos (documento básico, versión, tipo de sección) dentro de un presupuesto de latencia de ~300 ms para el tramo de retrieval (RNF-1: P95 total < 3 s). Presupuesto de infraestructura del proyecto de campo: < 20 €/mes. El despliegue de la API va en Railway, sin volúmenes persistentes garantizados entre deploys.

## Opciones consideradas

1. **FAISS en proceso** — Pros: latencia mínima (< 10 ms, sin red), cero coste, cero infraestructura. Contras: sin filtrado nativo por metadatos (habría que post-filtrar, degradando el recall del top-k); el índice vive en el filesystem del contenedor y Railway lo recrea en cada deploy, obligando a re-descargar el índice en el arranque; sin acceso concurrente desde un posible worker de ingestión.
2. **pgvector sobre el Postgres ya existente** — Pros: una pieza menos de infraestructura (ya hay Postgres para metadatos), filtrado SQL excelente, backups resueltos. Contras: en pruebas con 14k chunks el recall con HNSW fue equivalente a Qdrant, pero la instancia free de Railway (256 MB RAM) entra en swap con el índice HNSW cargado; subir de plan rompe el presupuesto.
3. **Qdrant Cloud free tier (1 GB)** — Pros: filtrado por payload nativo en la misma query ANN (sin post-filtrado), persistencia independiente de los deploys de la API, 1 GB sobra para 14k chunks con vectores de 1024 dims (~120 MB), latencia medida desde Railway: p50 45 ms / p95 110 ms. Contras: dependencia de un tercero y de la continuidad de su free tier; un salto de red añadido; el filtrado complejo (joins) no existe.

## Decisión

Opción 3, Qdrant Cloud. El criterio dominante es el **filtrado por metadatos dentro de la búsqueda ANN** (RF-4: filtrar por documento básico y versión), que FAISS no da y que pgvector solo da con una instancia de Postgres que no cabe en presupuesto. La persistencia independiente de los deploys elimina además la clase entera de bugs de "índice frío tras deploy".

## Consecuencias

- Positivas: retrieval con filtros en una sola llamada; re-indexar no toca la API; el dashboard de Qdrant sirve como herramienta de debugging de colecciones.
- Negativas / deuda asumida: vendor lock-in blando (mitigado: la interfaz de retrieval propia `Retriever.search()` es el único punto que conoce Qdrant); +45 ms de red por query; si el free tier desaparece, migración forzosa (~1 día a pgvector con plan de pago).
- Revisaríamos esta decisión si: el corpus superara ~500k chunks (el free tier se queda corto), o si el proyecto pasara a self-hosting completo por requisitos de datos (entonces pgvector o Qdrant en el propio clúster).
