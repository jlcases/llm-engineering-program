# Proyecto — Loop duradero de investigación

Construye un loop que investiga una pregunta técnica mediante varias fuentes, conserva evidencia y
termina con respuesta, abstención o escalado. Debe sobrevivir reinicios sin repetir descargas ni
acciones registradas.

## Objetivo

El sistema recibe una pregunta y debe:

- descomponerla en claims verificables;
- buscar fuentes permitidas dentro de un presupuesto;
- registrar evidencia y contradicciones;
- decidir si falta información útil;
- terminar con citas o abstención calibrada.

No se evalúa estilo de prosa. Se evalúan control, trazabilidad y comportamiento bajo fallos.

## Máquina mínima

```text
intake -> plan -> acquire -> assess -> answer
                    |         |
                    |         +-> needs_human
                    +-> retry / replan

any running state -> cancelled / exhausted / failed
```

Define el estado como schema versionado y cada arista como transición con guard y reducer.

## Presupuestos

Controla pasos, tiempo, tokens, coste, fuentes consultadas y concurrencia. Reserva antes de fan-out y
reconcilia con uso real. Una ampliación requiere un evento de autorización, no mutar el límite en
silencio.

## Durabilidad

Persiste journal y checkpoint. Toda adquisición recibe una identity key derivada de run, fuente y
consulta canónica. Al reanudar, reutiliza receipts o reconcilia antes de volver a llamar.

Prueba compatibilidad de schema y una migración. Un worker nuevo debe rechazar un checkpoint cuyo
significado de permisos haya cambiado.

## Fallos obligatorios

- 429 con `Retry-After`;
- timeout antes de enviar y después de aceptar;
- fuente que cambia de versión;
- dos fuentes autorizadas que se contradicen;
- planner que repite el mismo estado;
- cancelación durante fan-out;
- crash después de persistir intent y antes de receipt;
- budget agotado con evidencia parcial útil.

## Evaluación

Mide outcome, cobertura de claims, procedencia, pasos útiles, coste por respuesta, duplicación de
efectos, reanudación y escalado correcto. Conserva cada dimensión y segmenta por tipo de fallo.

Incluye planner y executors deterministas para CI. La evaluación con modelo es una capa adicional y
debe fijar modelo, harness, prompts y seed cuando exista.

## Entregables

- contrato de estado y tabla de transiciones;
- implementación del loop y executors simulados;
- journal, checkpoint y migración;
- idempotency ledger y reconciliación;
- suite de fallos y tests de terminales;
- dashboard o informe operativo;
- ADR sobre concurrencia y presupuesto;
- demo de crash y reanudación sin duplicación.

## Gate final

Detén el proceso en un punto elegido al azar durante cien ejecuciones. Tras reanudar, ninguna debe
quedar eternamente `running`, superar su presupuesto sin evento o duplicar un receipt. Documenta las
excepciones como fallos del diseño, no como «flakiness».
