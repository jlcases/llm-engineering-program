# 03 — Retrieval híbrido y evaluación

El grafo no sustituye al texto original. Añade estructura para recuperar relaciones y contexto
global, pero la respuesta debe volver a evidencia verificable.

## 1. Baseline antes del grafo

Construye primero retrieval léxico o vectorial y un dataset con tipos de consulta:

- factual local;
- relacional de uno o varios hops;
- agregación global;
- temporal;
- no respondible;
- conflicto entre fuentes.

El grafo se justifica solo en segmentos donde mejora una métrica de producto o reduce coste/riesgo.

## 2. Pipeline híbrido

Una estrategia común:

1. recuperar seeds por texto o vector;
2. mapear evidencia a entidades resueltas;
3. expandir predicados permitidos con hop y fan-out limitados;
4. puntuar paths por relevancia, autoridad, vigencia y coste;
5. recuperar pasajes que soportan las aristas elegidas;
6. rerankear el conjunto unido;
7. responder con evidence IDs y path explicable.

No entregues el subgrafo completo al modelo. Presupuesta nodos, aristas, tokens y tiempo.

## 3. GraphRAG global

Para preguntas sobre temas dominantes o relaciones a escala de corpus, GraphRAG extrae entidades y
relaciones, detecta comunidades y genera resúmenes jerárquicos. Es potente cuando una búsqueda local
no puede agregar la visión distribuida.

El coste de indexado, la sensibilidad a extracción y la pérdida de detalle en resúmenes obligan a
compararlo con alternativas simples. No lo uses como default para lookup factual.

## 4. Puntuar paths

Una función puede combinar:

```text
path_score = relevance * authority * freshness * provenance_coverage / traversal_cost
```

Evita multiplicar scores no calibrados sin entender su escala. Empieza con reglas interpretables,
evalúa y aprende pesos solo si el dataset lo permite.

Penaliza paths largos, predicados débiles y aristas derivadas de la misma fuente cuando necesitas
corroboración independiente.

## 5. Métricas

| Capa | Métricas |
|---|---|
| Extracción | mention F1, relation F1, type accuracy |
| Identidad | cluster precision/recall, unresolved rate |
| Retrieval | evidence recall@k, path recall, MRR, nDCG |
| Procedencia | claims con evidencia completa, fuentes autorizadas |
| Respuesta | faithfulness, completitud, abstención correcta |
| Operación | latencia, expansión, tokens, coste e invalidation lag |

Compara contra el baseline con el mismo dataset y presupuesto. Reporta segmentos y ejemplos donde
cada sistema gana.

## 6. Fallos característicos

- **Seed loss:** la entidad correcta nunca entra; el grafo no puede recuperarla.
- **Hub explosion:** un nodo popular consume el fan-out.
- **Wrong merge:** resolución incorrecta conecta dominios que no debían tocarse.
- **Stale edge:** una relación caducada domina el path.
- **Circular support:** claims derivados se citan entre sí sin fuente primaria.
- **Summary drift:** un resumen global sobrevive a la retirada de su evidencia.
- **Permission leak:** expansión atraviesa una arista no autorizada.

Diseña una señal y fallback para cada uno.

## 7. Decidir sin dogma

Mantén el grafo si mejora consultas importantes y su ganancia supera indexado, operación y riesgo.
Retíralo o limítalo a un segmento si el baseline iguala resultados. Graph Engineering incluye saber
cuándo no usar un grafo.
