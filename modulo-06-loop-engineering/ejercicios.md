# Ejercicios — Loop Engineering

Implementa los ejercicios con un planner determinista. Después, y solo después, conecta un modelo.
Así sabrás si el fallo pertenece al control o a la decisión.

## 1. Tabla de transiciones

Especifica una máquina con `running`, `succeeded`, `failed`, `exhausted`, `cancelled` y `needs_human`.
Para cada transición declara evento, guard, reducer y efecto permitido.

**Criterios de aceptación:**

- no existe transición implícita desde un terminal;
- todo `running` tiene próxima acción o alarma;
- guards incompatibles fallan en build o test;
- el motivo terminal es obligatorio;
- la tabla genera al menos un test por arista.

## 2. Presupuesto reservado

Ejecuta dos ramas concurrentes contra un presupuesto común. Primero reproduce el overspend con
check-then-act; después añade reserva y reconciliación atómicas.

Mide pasos, tokens, coste y capacidad. Demuestra que un fallo de una rama libera solo la reserva no
consumida.

## 3. Detector de progreso

Define una firma para una tarea de reparación de tests. Inyecta dos planes textualmente distintos que
no cambian el conjunto de tests fallidos.

El loop debe detectar estancamiento, probar una política alternativa una vez y terminar de forma
diagnóstica si no aparece evidencia nueva.

## 4. Matriz de errores

Implementa executors que devuelvan entrada inválida, conflicto, 429, timeout ambiguo, permiso denegado
y bug de invariante.

**Criterios de aceptación:**

- solo los errores transitorios consumen retry budget;
- conflicto fuerza lectura nueva antes de replanificar;
- permiso denegado nunca entra en backoff;
- timeout ambiguo consulta receipt;
- bug detiene el run y emite alerta estructurada.

## 5. Crash en la ventana crítica

Simula un proveedor que acepta un efecto y lanza una excepción antes de que el cliente reciba el
receipt. Reinicia el loop desde el checkpoint anterior.

Demuestra que la reconciliación encuentra el efecto por idempotency key y que el contador externo
permanece en uno.

## 6. Migración de checkpoint

Crea schema v1 y v2 con un cambio real de política. Implementa una migración pura y casos donde
reanudar deba rechazarse.

Entrega fixtures versionados, test de round trip, rechazo de campos desconocidos y decisión para
runs que no puedan migrarse con seguridad.

## 7. Cancelación y compensación

Cancela durante una acción lenta. Distingue:

1. acción no iniciada;
2. acción interrumpible;
3. efecto aceptado pendiente de receipt;
4. efecto confirmado con compensación posible;
5. efecto irreversible.

La compensación debe aparecer como nueva acción, nunca como borrado del journal.

## 8. SLO operativo del loop

Define panel y alertas para runs por estado, edad, razón terminal, reanudaciones, intents ambiguos y
pasos útiles. Incluye una consulta que detecte `running` sin alarma o trabajo pendiente.

Provoca un incidente y escribe un postmortem corto con señal inicial, impacto, timeline, causa y
cambio permanente.

## Entrega

Publica el diagrama o tabla de estados, código, journal de ejemplo, checkpoints v1/v2, tests felices y
adversos, métricas y postmortem. No incluyas una API key ni dependas de un proveedor para ejecutar CI.
