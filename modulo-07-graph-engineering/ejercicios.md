# Ejercicios — Graph Engineering

Cada ejercicio empieza con la consulta que debe mejorar. No se acepta «usar un grafo» como objetivo
sin baseline ni criterio de retirada.

## 1. Schema tipado

Modela servicios, modelos, políticas, ADRs y SLOs. Declara predicados permitidos, dirección,
cardinalidad y evidencia necesaria.

**Criterios de aceptación:**

- un endpoint de tipo incorrecto se rechaza;
- una arista factual sin evidence ID se rechaza;
- un ID repetido con propiedades incompatibles falla;
- existe una migración de schema probada;
- las queries siguen funcionando tras renombrar una etiqueta visual.

## 2. Resolución con zona incierta

Crea un dataset de nombres similares con `same`, `different` y `unresolved`. Combina clave oficial,
aliases y similitud contextual.

Reporta precision/recall de clusters, tasa `unresolved` y coste de revisión. Ajusta el umbral con una
función de coste que penalice más una fusión falsa que dejar dos entidades separadas.

## 3. Tiempo bitemporal

Representa una política que cambia hoy con vigencia retroactiva. Responde:

1. qué política era válida para un evento ayer;
2. qué habría respondido el sistema ayer con el conocimiento disponible;
3. qué respuesta debe producir hoy sobre aquel evento.

Incluye tests que impidan sobrescribir historia.

## 4. Procedencia de un claim

Construye el camino fuente → pasaje → claim → decisión → artefacto. Retira una fuente y propaga la
invalidación.

**Criterios de aceptación:**

- el artefacto derivado queda marcado stale;
- la auditoría conserva la decisión original;
- un nuevo build no usa el claim retirado;
- el sistema enumera qué elementos deben recalcularse.

## 5. Retrieval multi-hop

Diseña veinte preguntas relacionales y veinte factuales. Compara lexical, vector, graph y hybrid con
el mismo presupuesto de candidatos.

Reporta evidence recall, path recall, MRR, latencia y coste por segmento. No declares ganador global
si los tipos de consulta muestran trade-offs distintos.

## 6. Hub explosion

Introduce un nodo conectado a miles de vecinos. Implementa límites de fan-out, predicados y score,
además de una señal de truncación visible para el consumidor.

Demuestra que una respuesta no presenta el subgrafo truncado como completo.

## 7. Permission leak

Dos tenants comparten una entidad pública pero no sus relaciones privadas. Ejecuta una consulta que
intente atravesar del seed público a una arista del otro tenant.

La autorización debe aplicarse en cada hop y la traza debe conservar la política sin revelar el nodo
denegado.

## 8. ADR de retirada

Escribe un ADR con costes de indexado, operación, invalidación y evaluación. Define la mejora mínima
que justifica mantener el grafo y la fecha de revisión.

Incluye un caso donde una tabla o búsqueda híbrida simple sea la mejor alternativa.

## Entrega

Publica schema, fixtures, evaluador, tests de invariantes, resultados por segmento, paths con
procedencia y el ADR. Los datos deben ser ficticios o redistribuibles y no incluir información
personal real.
