# Módulo 06 — Loop Engineering

> Un agente no es «un LLM con tools». Es un loop que transforma estado bajo presupuestos, efectos y
> condiciones terminales.

El loop es donde los errores se acumulan: una decisión mediocre altera el estado que condiciona la
siguiente, un retry repite un efecto, una observación ambigua impide detectar progreso. Diseñarlo
como máquina de estados permite razonar sobre terminación, coste y recuperación antes de elegir un
framework.

## Qué aprenderás

1. Definir el contrato de una transición y estados terminales inequívocos.
2. Aplicar presupuestos simultáneos de pasos, tiempo, tokens, coste y efectos.
3. Separar retry, replanning, reflection y escalado humano.
4. Detectar estancamiento mediante señales externas de progreso.
5. Hacer efectos idempotentes y reanudar desde checkpoints compatibles.
6. Evaluar trayectorias bajo fallos, cancelación, concurrencia y backpressure.

## Mapa del módulo

| Paso | Lectura | Lab | Evidencia principal |
|---:|---|---|---|
| 1 | [`01-estado-presupuestos-y-terminacion.md`](teoria/01-estado-presupuestos-y-terminacion.md) | [`01_bounded_loop.py`](labs/01_bounded_loop.py) | Todos los caminos terminan de forma explicable |
| 2 | [`02-errores-idempotencia-y-reanudacion.md`](teoria/02-errores-idempotencia-y-reanudacion.md) | [`02_durable_loop.py`](labs/02_durable_loop.py) | Un efecto aceptado no se repite tras reinicio |
| 3 | [`03-progreso-concurrencia-y-evaluacion.md`](teoria/03-progreso-concurrencia-y-evaluacion.md) | Tests propios | Más iteraciones no sustituyen progreso |
| 4 | [`ejercicios.md`](ejercicios.md) | Inyección de fallos | Cancelación, agotamiento y errores conservan estado válido |
| 5 | [`proyecto/README.md`](proyecto/README.md) | Integración | El loop se puede operar y migrar |

## Estados terminales

| Estado | Significado | ¿Puede reanudarse? |
|---|---|---|
| `succeeded` | Outcome verificado | No, crea una nueva tarea si cambia el objetivo |
| `failed` | Fallo definitivo con causa | Solo desde una transición explícita de reparación |
| `exhausted` | Presupuesto consumido | Sí, con nueva autorización y presupuesto |
| `cancelled` | Señal externa atendida | Sí, si la política y los efectos lo permiten |
| `needs_human` | Falta autoridad o juicio | Sí, incorporando una decisión humana firmada |

## Prueba de trabajo

Entrega un loop duradero que:

- guarda estado y journal después de cada transición aceptada;
- comprueba presupuestos antes y después de una acción;
- detecta al menos un ciclo sin progreso;
- requiere idempotency key para efectos;
- reanuda sin repetir un receipt existente;
- atiende cancelación entre pasos;
- distingue éxito, imposibilidad, agotamiento, error y escalado;
- rechaza checkpoints de una versión incompatible.

Incluye tests para cada transición terminal y una prueba de crash en el punto más incómodo: después
de que el sistema externo acepte un efecto y antes de que el loop registre su receipt.

## Criterio de salida

Has completado el módulo cuando puedes dibujar el autómata, señalar qué estado persiste en cada
frontera de fallo y demostrar que ninguna ejecución queda en `running` para siempre. Si el control
depende de que el modelo «se dé cuenta», el loop aún no está diseñado.

## Fuentes primarias

- [Anthropic — Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)
- [LangGraph — Graph API overview](https://langchain-ai.github.io/langgraph/how-tos/state-reducers/)
- [LangGraph — Interrupts](https://langchain-ai.github.io/langgraph/concepts/breakpoints/)
