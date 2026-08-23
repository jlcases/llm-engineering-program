# 02 — Conocimiento, identidad y procedencia

Extraer entidades con un LLM es fácil. Mantener un grafo que no fusione personas distintas, no
presente relaciones caducadas como actuales y permita auditar cada claim es la parte de ingeniería.

## 1. Pipeline de conocimiento

Separa etapas y conserva sus outputs:

1. ingesta y versión de fuente;
2. segmentación con IDs estables;
3. extracción de menciones y relaciones candidatas;
4. normalización de tipos y predicados;
5. resolución de entidades;
6. validación de invariantes;
7. commit y actualización de índices;
8. evaluación sobre un conjunto etiquetado.

No escribas directamente el JSON del modelo en el grafo canónico. Trátalo como propuesta no
confiable.

## 2. Resolución de entidades

Usa señales en orden de autoridad:

- identificador oficial o clave de negocio;
- combinación determinista de atributos estables;
- diccionario de aliases revisado;
- similitud contextual calibrada;
- decisión humana para el intervalo ambiguo.

Define tres outcomes: `same`, `different` y `unresolved`. Forzar siempre una fusión convierte
incertidumbre visible en corrupción silenciosa.

## 3. Claims, no blobs de verdad

Representa una afirmación como objeto:

```json
{
  "claim_id": "claim:router:selects:luna:2026-08",
  "subject": "service:router",
  "predicate": "selects",
  "object": "model:luna",
  "valid_from": "2026-08-01",
  "valid_to": null,
  "evidence_ids": ["adr:007"],
  "status": "asserted"
}
```

Dos fuentes pueden soportar y contradecir el mismo claim. No resuelvas el conflicto con el score del
embedding; aplica autoridad, vigencia y política del dominio.

## 4. Tiempo bitemporal

Distingue:

- **valid time:** cuándo era cierta la relación en el mundo;
- **transaction time:** cuándo la conoció o registró el sistema.

Si una política publicada hoy corrige una vigencia que comenzó ayer, ambos tiempos difieren. Esta
separación permite reproducir qué habría respondido el sistema con el conocimiento disponible en una
fecha.

## 5. Procedencia de decisiones

Enlaza el path de conocimiento con la decisión:

```text
source -> passage -> claim -> graph path -> retrieved context -> decision -> effect
```

Cada salto registra versión y transformación. Si un resumen de comunidad interviene, enlázalo a los
claims que lo generaron y marca su algoritmo y fecha.

## 6. Corrección y retirada

No borres una arista publicada como si nunca hubiera existido. Registra supersession o invalidación,
actualiza índices de lectura y conserva auditoría. Propaga el cambio a claims, resúmenes y respuestas
materializadas derivados.

Un sistema sin lineage no sabe qué recalcular cuando una fuente cambia.

## 7. Evaluación de extracción y resolución

Mide por separado:

- precisión y recall de menciones;
- precisión de tipo;
- F1 de relaciones por predicado;
- precision/recall de clusters de entidad;
- cobertura de procedencia;
- frescura e invalidaciones propagadas;
- tasa y coste de revisión humana.

Segmenta por idioma, longitud, tipo de entidad y calidad de fuente. Una media alta puede esconder que
el sistema fusiona mal precisamente los nombres más importantes.

## 8. Seguridad

El grafo amplifica correlaciones. Aplica tenant y propósito en la consulta y en cada expansión, no
solo al seleccionar seeds. Evita inferir atributos sensibles a partir de caminos aunque cada nodo
aislado sea accesible.

Registra qué política autorizó cada path devuelto. «El agente lo encontró en el grafo» no es una
base de acceso.
