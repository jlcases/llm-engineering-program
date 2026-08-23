# 05 — Benchmarking causal de harnesses

Una tarea con un bug y una tabla de tiempos es un smoke test, no un benchmark. Sirve para comprobar
que el binario arranca y completa un bucle, pero no permite afirmar qué mecanismo funciona mejor ni
si el resultado se repetirá bajo presión de contexto, fallos de tools o reinicios.

Un benchmark de harnesses debe empezar por la afirmación que se pretende sostener. Después diseña
controles, tasks, instrumentación y análisis capaces de refutarla.

## 1. Tres preguntas, tres diseños distintos

| Modo | Pregunta válida | Condición mínima | Alcance de la conclusión |
|---|---|---|---|
| **Mecanismo** | ¿Qué loop o política gestiona mejor el mismo trabajo? | Misma capa, modelo, protocolo, superficie, autoridad y fixture | Diferencia atribuible al mecanismo controlado |
| **Outcome end-to-end** | ¿Qué sistema entrega mejor resultado operativo? | Task y budgets comunes; confounders declarados | Rendimiento del sistema completo bajo esas condiciones |
| **Composición** | ¿Qué aporta un orquestador alrededor de un runtime? | Runtime interior fijado y tratamiento on/off | Ganancia, coste y riesgo incremental de la composición |

No cambies de modo después de ver el resultado. Si Aider y Pi usan protocolos distintos, su outcome
puede compararse, pero no conviertas la diferencia en una conclusión sobre fiabilidad de tool
calling. Si Orca lanza cinco agentes y el baseline uno, reporta best-of-N y gasto total: no lo llames
una comparación uno-a-uno.

## 2. Constitución del benchmark

Antes del primer trial, versiona un documento con:

1. pregunta y claim permitido;
2. población de tasks y estrategia de muestreo;
3. candidatos, versión, configuración efectiva y superficie;
4. modelo, tokenizer, parámetros, endpoint y política de retry;
5. capabilities, schemas, approvals, sandbox y red;
6. budgets y condiciones terminales;
7. métricas primarias, secundarias y hard failures;
8. exclusiones de infraestructura decididas antes de observar resultados;
9. número de trials, orden, seeds y método de intervalo;
10. artefactos necesarios para una reproducción independiente.

Registrar después qué se midió permite seleccionar la historia que mejor queda. La constitución
convierte cambios razonables en cambios visibles y obliga a crear una nueva edición si alteran la
interpretación.

## 3. Una suite, no una única tarea

Incluye familias que ejerciten fronteras distintas:

| Familia | Capacidad bajo prueba | Fallo que debe revelar |
|---|---|---|
| Reparación acotada | Navegación, edición y verificación | Edit correcto sin outcome o diff fuera de alcance |
| Cambio sin test | Diseño de evidencia | Afirmar éxito sin crear una regresión comprobable |
| Búsqueda en repo grande | Selección y recuperación de contexto | Lectura indiscriminada, señal perdida o path inventado |
| Presión de contexto | Compaction y handoff | Olvido de constraints, repetición o latencia creciente |
| Tool malformada | Parser y política de recuperación | Loop bloqueado, retry ciego o argumentos mutados |
| Tool intermitente | Clasificación de errores | Repetir un fallo permanente o abandonar uno recuperable |
| Reinicio a mitad | Persistencia e idempotencia | Pérdida de estado o duplicación de efectos |
| Permiso denegado | Control de autoridad | Bypass, escalada silenciosa o falso éxito |
| Inyección en repo | Jerarquía de instrucciones | Exfiltración, cambio fuera de scope o tool peligrosa |
| Trabajo concurrente | Aislamiento | Cache, puertos, procesos o ficheros compartidos |

Cada familia necesita varios fixtures y al menos un caso negativo. Publicar exactamente las tasks
activas facilita overfitting; publica el generador, el contrato y una muestra, y conserva un conjunto
sellado para la edición competitiva. Los resultados deben seguir siendo auditables mediante hashes y
apertura posterior de la edición.

## 4. Variables que debes fijar

Para una comparación end-to-end, el lab exige ocho controles explícitos:

- `task_fixture`: estado inicial por hash o imagen inmutable;
- `model`: proveedor, ID y revisión exacta;
- `model_parameters`: temperatura, sampling, reasoning y límites;
- `starting_state`: historial, memoria, caches y ficheros iniciales;
- `tool_authority`: manifest, schemas, approvals y permisos del executor;
- `network_policy`: destinos permitidos y observación de conexiones;
- `time_budget`: reloj de servidor y política de timeout;
- `token_budget`: contabilidad comparable de input, output y cache.

También fija hardware cuando mides latencia local, orden de ejecución, carga concurrente y estado
térmico. Para backends remotos registra región y request IDs, pero no atribuyas toda variación al
harness si el proveedor no ofrece capacidad estable.

## 5. Instrumentación común

Normaliza eventos en el evaluation harness sin borrar el evento original. Cada adaptador debe
producir como mínimo:

```json
{
  "trial_id": "edition-03/task-041/pi/seed-2",
  "candidate": {"harness": "pi", "version": "pinned", "config_hash": "sha256:..."},
  "model": {"provider": "local", "id": "pinned", "parameters_hash": "sha256:..."},
  "event": {
    "sequence": 18,
    "kind": "tool_result",
    "capability": "run_tests",
    "monotonic_ms": 4821,
    "status": "retryable_error",
    "input_hash": "sha256:...",
    "output_preview": "redacted",
    "effect_receipt": null
  }
}
```

El adaptador puede mapear un bloque textual de Aider, un tool call nativo o una etapa de Orca, pero
debe conservar `raw_event_ref`. Si una métrica no existe para un protocolo, usa `not_applicable`; no
la conviertas en cero.

Registra además tiempo hasta primera acción útil, tiempo hasta primer outcome verificable, tokens por
paso, tamaño de contexto, eventos de compaction, tool calls inválidas, retries, intervención humana,
procesos y conexiones externas, diff, estado terminal y motivo.

## 6. Outcomes y taxonomía de fallo

El grader del estado final decide éxito funcional. Después clasifica por separado:

- `agent_failure`: el candidato recibió un trial válido y no consiguió el outcome;
- `policy_violation`: solicitó o produjo un efecto fuera de autoridad;
- `harness_failure`: parser, sesión, persistencia o executor rompieron el contrato;
- `evaluation_infra_error`: fixture, monitor, grader o cleanup impiden juzgar al candidato;
- `budget_exhausted`: el run alcanzó un límite definido sin estado de éxito;
- `human_abort`: una persona detuvo el run, conservando el motivo.

Un error de infraestructura no entra en el denominador de capacidad, pero sí en fiabilidad del banco.
Un policy violation no se compensa con rapidez ni con un test verde: es un hard failure.

## 7. Métricas sin una puntuación mágica

Publica componentes antes de cualquier agregado:

1. **Outcome rate:** éxitos sobre trials válidos, segmentados por familia.
2. **Harness reliability:** trials juzgables sobre trials programados.
3. **Policy compliance:** runs sin violaciones sobre runs válidos.
4. **Recovery rate:** errores inyectados de los que se recupera sin intervención.
5. **Efficiency conditional on success:** pasos, tokens, latencia y coste solo entre outcomes válidos.
6. **Context degradation:** cambio entre inicio y cola en precisión, TTFT y repetición.
7. **Human load:** approvals, aclaraciones, selección, revisión y minutos de merge.
8. **Effect integrity:** receipts únicos, ausencia de duplicados y cleanup confirmado.

La velocidad solo es buena condicionada a corrección y seguridad. Un agente que termina rápido porque
abandona o salta verificaciones no es eficiente. Para comparaciones pareadas, reporta la distribución
de diferencias por task y un intervalo; para tasas, muestra numerador, denominador e intervalo. No
ocultes colas con una media.

Si el producto necesita un gate, aplica primero restricciones duras y luego una función explícita:

```text
eligible = outcome_ok and policy_ok and no_duplicate_effect and trace_complete
utility  = task_value - compute_cost - human_cost - orchestration_cost
```

No existe una utilidad universal. Publica los componentes para que otra organización pueda aplicar
sus propios costes y riesgos.

## 8. Diseño pareado y orden de ejecución

Ejecuta cada fixture con cada candidato y aleatoriza el orden dentro de bloques. Así, una task difícil
afecta a todos y no se confunde con el candidato. Alterna candidatos para reducir drift de backend,
calentamiento de cache y temperatura de hardware.

Los trials deben partir de clones o imágenes nuevos. No uses `git checkout . && git clean -fd` como
única garantía si existen ficheros ignorados, caches fuera del repo, bases de datos, procesos o
memoria persistente. Calcula un hash del estado inicial y comprueba el cleanup mediante un inventario
posterior.

Para sistemas no deterministas, ejecuta repeticiones planificadas. Una seed no vuelve determinista un
proveedor remoto ni un scheduler concurrente; solo identifica una condición. Conserva todas las
repeticiones, no solo la mejor.

## 9. Pruebas especiales por arquitectura

### Compaction

Construye una tarea por fases con constraints antiguos que vuelven a ser relevantes al final. Inyecta
observaciones largas pero irrelevantes y un error que fuerce replanificación. Compara no solo tokens,
sino retención de constraints, evidencia descartada, duplicación y TTFT antes y después de compactar.

### Memoria persistente

Usa pares de tasks isomorfas con datos y respuestas distintos. Audita qué entradas se escriben y qué
se recupera. Añade un canary que nunca debe persistir y una petición de borrado. El beneficio del
segundo pase solo cuenta si el canary no reaparece y la limpieza es verificable.

### Orquestación paralela

Fija el runtime interior. Compara uno contra N con presupuesto total, wall time, outcome del candidato
elegido, calidad de selección y minutos de merge. Incluye un caso donde dos worktrees modifican el
mismo área y otro donde comparten un servicio externo para demostrar que Git no es todo el sandbox.

### Flujos deterministas

Interrumpe después de un efecto confirmado y reanuda. La etapa completada no debe repetirse. Cambia
el modelo de un rol sin cambiar el resto y comprueba que configuración, commits y progress log
permiten atribuir la diferencia.

## 10. Fallos inyectados obligatorios

La suite del propio benchmark debe probar:

- JSON de tool truncado, argumentos extra y tipo incorrecto;
- timeout antes y después de aplicar un efecto;
- proceso hijo que sobrevive a su padre;
- output que excede el límite y contiene un secreto canary;
- endpoint que devuelve `429`, `500`, respuesta vacía y stream cortado;
- approval expirado, reutilizado o vinculado a otros argumentos;
- grader que discrepa del texto final;
- cleanup parcial y fixture con hash incorrecto.

El happy path demuestra que el banco puede producir un número. Estos casos demuestran si ese número
merece confianza.

## 11. Paquete de evidencia

Una edición reproducible publica:

- constitución y changelog de la edición;
- generador de tasks, muestras abiertas y hashes del conjunto sellado;
- imágenes o lockfiles del entorno;
- configuraciones efectivas redactadas y sus hashes;
- adaptadores, schema de eventos y tests de conformidad;
- trayectorias redactadas, outcomes y artefactos finales;
- resultados trial a trial, exclusiones y logs de infraestructura;
- script de análisis que reconstruye tablas desde datos crudos;
- revisión manual de una muestra de éxitos, fallos y desacuerdos.

El leaderboard es una vista derivada, nunca la fuente de verdad. Si solo conservas la clasificación,
no podrás explicar una regresión cuando cambien el modelo, el loop o la política de tools.

## Gate de salida

Tu benchmark está listo cuando un tercero puede añadir un harness, ejecutar una task nueva, provocar
un fallo de infraestructura y obtener la misma clasificación causal sin modificar el agregador.
También debe poder demostrar por qué Pi–OpenCode es una comparación de mecanismo, Aider–Pi es una
comparación end-to-end con protocolos distintos y Orca de stablyai–Pi es una prueba de composición.
