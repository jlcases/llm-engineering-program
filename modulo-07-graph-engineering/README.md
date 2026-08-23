# Módulo 07 — Graph Engineering

> Un grafo aporta valor cuando la relación forma parte de la respuesta o del control. Si solo cambia
> el dibujo de cajas, añade complejidad sin añadir evidencia.

Este módulo separa tres planos que suelen mezclarse: el grafo de ejecución decide qué paso ocurre; el
grafo de conocimiento representa entidades y relaciones del dominio; el grafo de procedencia conecta
claims y decisiones con la evidencia que los justifica. Pueden colaborar, pero tienen schemas,
invariantes y métricas diferentes.

## Qué aprenderás

1. Elegir entre tabla, documento, vector y grafo según el patrón de consulta.
2. Diseñar identidad, tipos de nodo y arista, cardinalidad e invariantes.
3. Modelar ejecución con estado, reducers, ciclos, interrupciones y checkpoints.
4. Construir conocimiento con resolución de entidades y evolución temporal.
5. Conservar procedencia a nivel de claim, relación y decisión.
6. Evaluar retrieval híbrido y demostrar cuándo el grafo supera al baseline.

## Mapa del módulo

| Paso | Lectura | Lab | Pregunta de revisión |
|---:|---|---|---|
| 1 | [`01-tres-grafos-y-sus-invariantes.md`](teoria/01-tres-grafos-y-sus-invariantes.md) | [`01_typed_provenance_graph.py`](labs/01_typed_provenance_graph.py) | ¿Qué significa cada nodo y qué relación está permitida? |
| 2 | [`02-conocimiento-identidad-y-procedencia.md`](teoria/02-conocimiento-identidad-y-procedencia.md) | Tests propios | ¿Qué evidencia y versión sostienen cada edge? |
| 3 | [`03-retrieval-hibrido-y-evaluacion.md`](teoria/03-retrieval-hibrido-y-evaluacion.md) | [`02_hybrid_graph_retrieval.py`](labs/02_hybrid_graph_retrieval.py) | ¿El camino mejora una consulta real? |
| 4 | [`ejercicios.md`](ejercicios.md) | Casos adversos | ¿Cómo falla identidad, frescura o procedencia? |
| 5 | [`proyecto/README.md`](proyecto/README.md) | Integración | ¿El sistema puede explicar qué sabe y qué hizo? |

## Tres planos

| Plano | Nodos típicos | Aristas típicas | Métrica principal |
|---|---|---|---|
| Ejecución | Estados, tareas, tools | transición, dependencia, delegación | terminación y corrección de transición |
| Conocimiento | Entidades, eventos, conceptos | pertenece, causa, usa, ocurrió antes | precisión y cobertura de relaciones |
| Procedencia | Claims, fuentes, versiones, decisiones | soporta, contradice, deriva de | cobertura y fidelidad de evidencia |

No metas las tres cosas en una tabla genérica `nodes/edges` sin tipos. Compartir motor de almacenamiento
no obliga a compartir semántica.

## Prueba de trabajo

Entrega un sistema que:

- valida tipos, endpoints y cardinalidad antes de escribir;
- rechaza una relación sin evidencia estable;
- resuelve dos menciones de la misma entidad y conserva la decisión;
- representa tiempo o versión sin sobrescribir historia;
- combina retrieval textual con una expansión de grafo acotada;
- devuelve paths junto con evidence IDs;
- compara precisión, cobertura, latencia y coste contra un baseline sin grafo;
- muestra un caso donde el grafo perjudica y activa fallback.

## Criterio de salida

Has completado el módulo cuando puedes borrar la capa de grafo, ejecutar el mismo dataset y explicar
con métricas qué capacidad se pierde y qué coste desaparece. Si no existe diferencia medible, el
grafo no está justificado.

## Fuentes primarias

- [Microsoft Research — Project GraphRAG](https://www.microsoft.com/en-us/research/project/graphrag/)
- [LangGraph — Graph API overview](https://langchain-ai.github.io/langgraph/how-tos/state-reducers/)
- [LangGraph — Persistence and interrupts](https://langchain-ai.github.io/langgraph/concepts/breakpoints/)
