# 03 — Trazas y evaluation harness

Evaluar solo el texto final oculta la mayoría de fallos importantes. Un agente puede escribir una
respuesta correcta después de modificar el recurso equivocado, repetir un pago o consultar datos que
no tenía permiso para leer.

## 1. Trajectory y outcome

Conserva dos vistas complementarias:

- **Trajectory:** decisiones observables, tool calls, resultados, errores y transiciones.
- **Outcome:** estado verificable del entorno cuando el run termina.

La trajectory explica cómo llegó. El outcome confirma si realmente llegó. Ninguna sustituye a la
otra.

## 2. Esquema mínimo de evento

```json
{
  "run_id": "run-01",
  "sequence": 7,
  "kind": "tool_result",
  "capability": "create_ticket",
  "elapsed_ms": 142,
  "effect_receipt": "ticket:1842",
  "payload_preview": {"status": "created"},
  "policy_version": "effects-v3"
}
```

Usa tiempo monotónico para duraciones y tiempo UTC para correlación externa. La secuencia debe ser
estable incluso si varias tools terminan en paralelo. No persistas razonamiento privado; registra
decisiones, alternativas declaradas y evidencia suficiente para auditar comportamiento.

## 3. Anatomía de una evaluación

Una evaluación útil separa:

1. **Task set:** distribución de capacidades y fallos que importa al producto.
2. **Fixture:** estado inicial reproducible.
3. **Trial runner:** harness, modelo, versiones, budgets y aislamiento.
4. **Graders:** reglas deterministas, modelos evaluadores y revisión humana cuando proceda.
5. **Aggregator:** intervalos, segmentos y muestras; no solo una media.
6. **Failure review:** taxonomía que convierte fallos en cambios concretos.

Ejecuta varios trials cuando exista variabilidad. Reporta el denominador, la dispersión y la versión
exacta del entorno; un `83 %` sin ellos es decoración.

## 4. Diseñar graders independientes

Combina tres clases:

| Grader | Bueno para | Riesgo principal |
|---|---|---|
| Determinista | Schema, estado DB, tests, permisos, coste | Medir un proxy demasiado estrecho |
| Modelo evaluador | Semántica, cobertura, tono, utilidad | Sesgo, leniencia y no reproducibilidad |
| Humano | Criterio experto, taste, casos ambiguos | Coste y variación entre revisores |

No pidas al mismo agente que produzca y otorgue la única nota. Cuando uses un judge, calibra contra
ejemplos humanos, fija su prompt y versión, oculta la identidad del candidato y revisa desacuerdos.

## 5. Resultado final frente a proceso

Puntúa por separado:

- éxito del outcome;
- eficiencia de pasos, tokens, coste y latencia;
- cumplimiento de permisos y approvals;
- recuperación ante errores inyectados;
- duplicación de efectos;
- calidad de la respuesta al usuario.

Un agregado puede servir como gate, pero conserva los componentes. Si una optimización gana calidad
a costa de duplicar efectos, la media no debe esconderlo.

## 6. Casos negativos del propio harness

Prueba también la infraestructura de evaluación:

- fixture que no puede crearse;
- trial que excede timeout y deja procesos hijos;
- grader que falla o devuelve una forma inválida;
- dos trials que escriben el mismo recurso;
- resultado parcial tras cancelación;
- cache caliente que cambia el segundo intento;
- trace truncada antes del evento que explica el fallo.

El harness debe marcar el resultado como error de infraestructura, no como fallo de capacidad del
agente. Mezclarlos contamina cualquier decisión de modelo o arquitectura.

## 7. Del fallo a una mejora

Clasifica cada muestra fallida por la frontera responsable: contexto ausente, capability ausente,
descripción ambigua, permiso incorrecto, executor defectuoso, loop sin control, grader erróneo o
limitación del modelo. Después corrige la capacidad del sistema, añade el caso a regresión y vuelve a
ejecutar el segmento afectado y un conjunto canary.

Una eval suite útil acumula memoria institucional. Una suite que solo produce una cifra acumula
gráficos.
