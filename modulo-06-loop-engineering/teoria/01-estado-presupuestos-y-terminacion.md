# 01 — Estado, presupuestos y terminación

El loop mínimo observa estado, decide, actúa y vuelve a observar. La versión profesional añade un
contrato de transición, presupuestos verificables y una función terminal que no depende de texto
optimista del modelo.

## 1. Contrato de transición

Modela cada paso como:

```text
transition(state, observation, budgets, policy) -> decision
execute(decision) -> action_result
reduce(state, decision, action_result) -> next_state
```

`transition` puede usar un modelo. `execute` y `reduce` protegen las invariantes. Separarlos permite
reproducir una decisión, simular tools y comprobar que el reducer no acepta una forma inválida.

## 2. Estado explícito

El estado incluye únicamente datos necesarios para continuar:

- identidad de run, task y versión;
- objetivo y restricciones vigentes;
- observación normalizada más reciente;
- artefactos y receipts estables;
- uso acumulado de presupuestos;
- marcador de progreso;
- decisiones humanas pendientes o incorporadas;
- estado terminal y motivo, cuando existan.

No guardes clientes HTTP, conexiones ni objetos no serializables. Guarda identidad y reconstruye
recursos al reanudar.

## 3. Presupuesto multidimensional

Un único `max_steps` no limita un paso que abre cien procesos o gasta todo el presupuesto de tokens.
Controla al menos:

| Dimensión | Se comprueba | Señal terminal |
|---|---|---|
| Pasos | Antes de decidir y tras aceptar transición | `step_budget` |
| Tiempo monotónico | Antes y después de cada operación | `time_budget` |
| Tokens | Al reservar y reconciliar uso real | `token_budget` |
| Coste | Con precio versionado y receipt real | `cost_budget` |
| Efectos | Antes de una escritura externa | `effect_budget` |
| Concurrencia | Al admitir trabajo en cola | `capacity_budget` |

Reserva antes de ejecutar y reconcilia después. Sin reserva, dos acciones concurrentes pueden
comprobar el mismo saldo y excederlo juntas.

## 4. Función terminal

Evalúa condiciones en orden estable:

1. cancelación o revocación de autoridad;
2. violación de seguridad;
3. outcome de éxito verificado;
4. imposibilidad demostrada;
5. necesidad de juicio humano;
6. presupuesto agotado;
7. siguiente transición.

El orden importa. Si un pago se confirmó y al mismo tiempo venció el tiempo, el outcome puede ser
éxito aunque el presupuesto esté agotado. Define la semántica del producto y pruébala.

## 5. Éxito como estado externo

No aceptes `{"done": true}` del modelo como única prueba. Consulta el sistema relevante:

- existe la fila y tiene la versión esperada;
- el fichero cambió y los tests pasan;
- el ticket remoto devuelve un receipt;
- la respuesta cita evidencia permitida;
- no se produjo ningún efecto adicional.

El modelo puede proponer que terminó; el harness verifica el outcome y el loop transiciona.

## 6. Imposibilidad y escalado

Una tarea imposible no debe consumir presupuesto hasta parecer un timeout. Define señales como
credencial ausente, conflicto de políticas, dependencia permanentemente no disponible o necesidad de
una decisión legal. Termina en `failed` o `needs_human` con evidencia y opciones concretas.

Escalar no es pedir «¿qué hago?». Incluye el estado mínimo, la decisión bloqueada, alternativas,
riesgo, coste y la acción exacta que una persona puede autorizar.

## 7. Invariantes de un loop acotado

- cada transición incrementa una secuencia persistida;
- todo estado `running` tiene una próxima acción o una alarma;
- todo presupuesto tiene unidad, fuente y política de reconciliación;
- ningún estado terminal vuelve a ejecutar una transición implícita;
- cada efecto tiene identidad antes de invocarse;
- cancelación no borra evidencia de pasos aceptados.

Si no puedes demostrar estas invariantes con tests, el loop es una convención, no un sistema de
control.
