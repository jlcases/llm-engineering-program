# 03 — Progreso, concurrencia y evaluación del loop

Terminar dentro del presupuesto no demuestra que el loop sea bueno. Debe avanzar hacia el outcome,
usar concurrencia sin romper invariantes y degradarse de manera diagnóstica cuando el mundo no
coopera.

## 1. Señales de progreso

El contador de pasos mide actividad, no progreso. Define marcadores externos al texto del modelo:

- tests fallidos que pasan de cinco a dos;
- entidades pendientes que bajan de cien a veinte;
- cobertura de evidencia que aumenta;
- estado remoto que avanza de `queued` a `accepted`;
- incertidumbre calibrada que disminuye con nueva evidencia.

Normaliza el marcador para detectar estados equivalentes. Dos planes redactados de forma distinta
pueden representar el mismo punto muerto.

## 2. Ciclos improductivos

Conserva una firma de estado y acción. Si reaparece sin nueva evidencia, aplica una política:

1. primer ciclo: resume el bloqueo y exige una alternativa;
2. segundo ciclo: cambia capability, reduce alcance o solicita una observación distinta;
3. ciclo final: termina en `exhausted` o `needs_human`.

Aumentar `max_steps` ante un ciclo solo encarece el mismo fallo.

## 3. Concurrencia con estructura

Paraleliza trabajos independientes, no decisiones que escriben el mismo estado sin reducer. Para
cada fan-out define:

- conjunto de inputs inmutable;
- límite de workers y cola;
- presupuesto reservado por rama;
- orden o clave de agregación;
- política de fallo parcial;
- cancelación de ramas cuando ya existe outcome suficiente.

El reducer debe ser asociativo y, si el orden no importa, conmutativo. De lo contrario, serializa o
registra el orden como parte del contrato.

## 4. Backpressure

El loop no debe crear trabajo más rápido de lo que executors y sistemas externos pueden absorber.
Controla admisión mediante semáforos, tamaño de cola y cuotas por tenant. Propaga 429 y señales de
carga al planner como estado, no como texto que invite a insistir.

Mide tiempo en cola por separado de tiempo de ejecución. Una latencia alta por backpressure no se
arregla eligiendo un modelo más rápido.

## 5. Calidad de trayectoria

Evalúa dimensiones separadas:

| Dimensión | Métrica ejemplo |
|---|---|
| Outcome | Tasa de tareas verificadas |
| Progreso | Pasos útiles / pasos totales |
| Eficiencia | Tokens, coste y tiempo por éxito |
| Robustez | Éxito bajo errores inyectados |
| Seguridad | Violaciones y efectos no aprobados |
| Durabilidad | Reanudaciones correctas / crashes |
| Intervención | Escalados correctos y evitables |

Segmenta por tipo de tarea y fallo. Una media puede ocultar que el loop funciona para lectura pero
duplica escrituras bajo timeout.

## 6. Simulación determinista

Antes de gastar tokens, ejecuta el loop con planners y executors programados:

- secuencia feliz;
- error transitorio seguido de éxito;
- permiso permanente denegado;
- observación repetida;
- cancelación entre dos acciones;
- crash en la ventana de ambigüedad;
- checkpoint antiguo;
- dos ramas que compiten por presupuesto.

La simulación prueba el control. Las evals con modelos prueban decisiones dentro de ese control. Si
mezclas ambas capas, cada fallo resulta más caro y menos localizable.

## 7. Operar el loop

Expón métricas de runs por estado, edad de `running`, razón terminal, pasos, coste, receipts pendientes
y reanudaciones. Alerta sobre estados imposibles: runs sin próxima alarma, intents ambiguos demasiado
antiguos o secuencias que retroceden.

La vista operativa debe responder en minutos: qué está atascado, qué efecto puede estar incierto y
qué versión produjo el comportamiento.
