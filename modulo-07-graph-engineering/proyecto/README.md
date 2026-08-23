# Proyecto — Mapa operativo con conocimiento y procedencia

Construye un sistema que responde preguntas sobre la arquitectura de un producto: qué servicio usa
qué modelo, qué política lo limita, qué ADR justificó la decisión y qué evidencia sigue vigente.

## Preguntas objetivo

Incluye al menos:

- cinco lookups factuales;
- cinco preguntas relacionales de dos o más hops;
- cinco preguntas temporales;
- cinco preguntas globales o de agregación;
- cinco casos no respondibles o con fuentes en conflicto.

Etiqueta evidence IDs y paths esperados antes de ajustar el sistema.

## Tres grafos

1. **Ejecución:** pipeline de ingesta, validación, indexado y consulta.
2. **Conocimiento:** servicios, modelos, equipos, políticas, decisiones y relaciones.
3. **Procedencia:** fuentes, pasajes, claims, versiones y artefactos derivados.

Puedes usar un solo motor, pero los schemas y permisos deben permanecer separados.

## Ingesta

Procesa ADRs, SLOs y un catálogo ficticio de servicios. Conserva hash y fecha de cada fuente, extrae
propuestas, resuelve identidad y valida antes de commit.

Añade una cola de revisión para relaciones inciertas. No fuerces al modelo a decidir cuando la señal
está dentro de la zona ambigua.

## Consulta

Compara cuatro rutas: lexical, vector, graph y hybrid. La respuesta devuelve:

- texto o abstención;
- evidence IDs;
- path de entidades y predicados;
- vigencia y conflictos;
- señal de truncación;
- versión de política de acceso.

## Cambio y lineage

Corrige un ADR, retira una fuente y cambia una política con vigencia retroactiva. El sistema debe
identificar qué claims, resúmenes e índices quedan stale y reconstruir solo lo necesario.

Conserva qué habría respondido la versión anterior.

## Casos adversos

- dos entidades con el mismo nombre;
- alias que cambia con el tiempo;
- arista sin evidencia;
- ciclo prohibido;
- hub con fan-out extremo;
- resumen global stale;
- path que cruza tenant;
- seed correcto ausente del primer retrieval.

## Evaluación

Mide extracción, resolución, evidence recall, path recall, faithfulness, abstención, latencia, coste,
fan-out e invalidation lag. Segmenta por tipo de consulta y compara contra el baseline.

## Entregables

- schemas de los tres planos e invariantes;
- dataset ficticio y etiquetas;
- pipeline de ingesta con revisión;
- cuatro retrievers bajo interfaz común;
- respuestas con path y procedencia;
- suite adversa y resultados segmentados;
- lineage e invalidación incremental;
- ADR de adopción o retirada del grafo;
- demo de una corrección propagándose hasta la respuesta.

## Gate final

Elimina el grafo de conocimiento y vuelve a ejecutar el dataset. La defensa debe mostrar qué queries
empeoran, cuánto, por qué y a qué coste se obtenía la mejora. Si no puedes responder esas cuatro
preguntas, la decisión arquitectónica no está sustentada.
