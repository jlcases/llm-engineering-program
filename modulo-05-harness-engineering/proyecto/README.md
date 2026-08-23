# Proyecto — Harness de reparación verificable

Construye un harness para un agente que recibe un repositorio pequeño con un bug, localiza la causa,
propone un cambio y demuestra la reparación. El objetivo no es maximizar autonomía, sino demostrar
que el entorno hace visible y controlable cada decisión relevante.

## Escenario

Prepara al menos doce tasks distribuidas entre:

- fallo localizado con test existente;
- fallo sin test de regresión;
- petición fuera de alcance;
- dependencia o servicio no disponible;
- instrucción maliciosa dentro del repositorio;
- cambio que requeriría una acción externa no autorizada.

Cada task parte de un fixture inmutable y se ejecuta en un workspace desechable.

Selecciona dos runtimes de la misma cohorte del catálogo. Añade después un orquestador compatible
como tratamiento opcional alrededor de uno de ellos. Escribe antes de ejecutar qué claim corresponde
a la comparación de mecanismo y cuál a la composición.

## Constitución de la edición

Congela modelo, parámetros, versión de cada runtime, superficie, manifest de tools, approvals,
sandbox, red, budgets y estado inicial. Publica el orden aleatorizado, repeticiones, métricas y reglas
de exclusión antes de observar resultados.

El conjunto activo tendrá fixtures sellados. Publica el generador, al menos dos ejemplos y hashes de
todos los casos; abre los fixtures restantes cuando cierres la edición.

## Arquitectura mínima

```text
Landscape + Constitution -> Task registry -> Fixture builder
                                                  |
Candidate adapter -> Agent harness -> Isolated workspace + Capability executors
                           |
                           +----------> Normalized trace + Raw event references

Structured trace + Final workspace -> Graders -> Trial report
```

Separa el modelo mediante una interfaz para poder ejecutar un planner determinista en CI y uno real
en una evaluación opcional.

## Capacidades

Incluye lectura, búsqueda, edición y ejecución de comandos permitidos. Modela cada una con:

- schema estricto;
- alcance de filesystem o proceso;
- clase de efecto;
- timeout y límite de output;
- errores tipados;
- política de aprobación y retry.

No expongas shell arbitraria si los escenarios pueden resolverse con comandos acotados. Si decides
exponerla, documenta por qué y aplica aislamiento de proceso, red, variables y volumen.

## Evaluación

Mide al menos:

1. outcome funcional;
2. regresión del resto de tests;
3. diff dentro del alcance;
4. cumplimiento de capabilities y approvals;
5. ausencia de secretos en trazas;
6. pasos, tokens, latencia y coste;
7. errores de infraestructura separados de fallos del agente;
8. recuperación ante fallos inyectados y degradación bajo presión de contexto;
9. intervención humana, duplicación de efectos y cleanup;
10. coste incremental y calidad de selección del tratamiento de orquestación.

Ejecuta varios trials para los casos no deterministas. Publica intervalos y muestras, no una cifra
sin denominador. La velocidad solo se interpreta entre trials correctos y seguros.

No produzcas una única puntuación opaca. Publica outcome rate por familia, fiabilidad del harness,
policy compliance, recovery rate y eficiencia condicionada a éxito. Si añades una utilidad para
ordenar candidatos, conserva cada componente y sus unidades.

## Casos adversos obligatorios

- path traversal y symlink hacia fuera;
- comando fuera de allowlist;
- output de proceso que supera el límite;
- timeout con proceso hijo;
- cache o artefacto de otro trial;
- tool que afirma éxito sin producir outcome;
- intento de escribir un comentario externo sin aprobación;
- reinicio después de un efecto confirmado;
- endpoint con stream truncado y error recuperable;
- dos candidatos que colisionan en Git o en un servicio compartido;
- contexto largo donde una constraint inicial vuelve a ser necesaria al final.

## Entregables

- contrato versionado de task, capability, trace y outcome;
- runner aislado con cleanup garantizado;
- agent harness con manifest y política de autoridad;
- evaluation harness con graders independientes;
- suite de tasks y tests de infraestructura;
- catálogo validado, constitución de edición y adaptadores por candidato;
- informe de resultados y taxonomía de fallos;
- datos trial a trial y script que reconstruye todas las tablas;
- ADR sobre la capability más potente del sistema;
- vídeo corto donde un caso feliz y uno adverso recorren la misma instrumentación.

## Gate final

Una persona revisora cambia el modelo por un stub, añade una task y provoca el fallo de una tool. Si
puede localizar el problema y repetir el trial sin leer el código interno del runner, el harness es
legible. Si necesita interpretar logs libres o limpiar estado a mano, todavía no está terminado.

Como defensa final, esa persona debe cambiar una comparación Pi–OpenCode por Pi–Aider y por
Pi–Orca(stablyai). El sistema debe cambiar el alcance del claim o rechazarlo sin que se modifique el
agregador. Ese comportamiento demuestra que el benchmark conserva causalidad, no solo números.
