# 01 — Anatomía de un harness y sus contratos

Cambiar el prompt no arregla un entorno opaco. Cuando un agente no encuentra una fuente, interpreta
mal una tool o no puede comprobar su trabajo, el problema suele estar en el sistema que media entre
el modelo y el mundo.

## 1. Cuatro piezas que no deben mezclarse

| Pieza | Responsabilidad | No debería decidir |
|---|---|---|
| **Modelo** | Propone decisiones a partir del contexto disponible | Permisos reales ni éxito del efecto |
| **Agent harness** | Ensambla contexto, expone capacidades, ejecuta tools y mantiene estado | La verdad de una afirmación sin evidencia |
| **Producto** | Define autoridad, UX, políticas y efectos permitidos | Cómo puntúa una evaluación interna |
| **Evaluation harness** | Prepara tareas, aísla trials, registra y aplica graders | Qué capacidades recibe producción |

El mismo modelo dentro de dos harnesses distintos es dos agentes distintos. También lo es el mismo
harness con otra versión de tools, permisos o política de contexto. Por eso un resultado debe fijar
ambas identidades.

```text
agent_identity = hash(model_contract, harness_version, capability_manifest, policy_version)
```

## 2. Task contract

Una tarea operable necesita más que una instrucción:

```json
{
  "task_id": "repair-api-017",
  "instruction": "Repair the failing endpoint and prove the regression is fixed",
  "initial_state": "fixture:v3",
  "allowed_capabilities": ["read_repo", "edit_workspace", "run_tests"],
  "budgets": {"steps": 12, "seconds": 600, "external_effects": 0},
  "success": ["target_test_passes", "full_suite_not_worse", "diff_within_scope"]
}
```

`success` describe outcomes verificables, no una frase que el agente pueda afirmar. Si el agente
dice que un test pasa pero el proceso devuelve código distinto de cero, manda el estado del entorno.

## 3. Capability contract

Cada capacidad necesita como mínimo:

- nombre estable y descripción orientada a decisión;
- esquema estricto de entrada y salida;
- clase de efecto: lectura, escritura reversible, escritura externa o irreversible;
- autoridad necesaria y condición de aprobación;
- timeout, tamaño máximo, errores tipados y política de retry;
- observación que devuelve y datos que nunca deben entrar en la traza.

Una tool que devuelve texto libre obliga al modelo a adivinar si hubo éxito. Es preferible:

```json
{"ok": false, "error": {"code": "STALE_VERSION", "retryable": false, "current": 18}}
```

que:

```text
Something went wrong. Try again.
```

## 4. Run y estado terminal

Todo run debe terminar en un estado enumerado. Como mínimo:

- `succeeded`: el outcome cumple el contrato;
- `failed`: existe un fallo definitivo y diagnosticado;
- `exhausted`: se consumió un presupuesto antes de completar;
- `cancelled`: una señal externa detuvo la ejecución;
- `needs_human`: falta autoridad o juicio no delegable.

No uses `completed` como sinónimo de éxito: una ejecución puede completar su lifecycle y terminar
agotada. El estado final conserva motivo, uso de presupuestos, última evidencia y artefactos.

## 5. Versionar lo que cambia el comportamiento

Registra por separado:

1. modelo y parámetros;
2. versión del agent harness;
3. manifiesto de capabilities;
4. política de permisos;
5. fixtures y versión del entorno;
6. versión de cada grader.

Un aumento de puntuación sin esa matriz no permite saber qué mejoró. Tampoco compares trials si uno
vio un fichero, cache o commit que el otro no podía ver.

## 6. Invariantes antes que instrucciones

Una instrucción dice «no escribas fuera del workspace». Una invariante resuelve el path, comprueba
que pertenece a la raíz permitida y rechaza la llamada antes de tocar disco. Usa instrucciones para
orientar decisiones e invariantes para proteger límites.

La regla de diseño es sencilla: si una condición puede verificarse de forma determinista en la
frontera, no la delegues al modelo.
