# 02 — Errores, idempotencia y reanudación

Los fallos difíciles ocurren entre sistemas: el proveedor acepta una acción, la red se corta antes
del response y el loop no sabe si debe repetir. Ningún prompt resuelve esa ambigüedad; hacen falta
identidad, receipts y una política de reconciliación.

## 1. Taxonomía antes de retry

Clasifica el error en la frontera que lo conoce:

| Clase | Ejemplo | Respuesta |
|---|---|---|
| Entrada inválida | Schema o ID incorrecto | Reparar una vez o fallar; no backoff |
| Conflicto | Versión obsoleta | Leer estado nuevo y replanificar |
| Transitorio | 429 o timeout antes de enviar | Retry acotado con jitter |
| Ambiguo | Timeout después de enviar | Consultar por idempotency key |
| Permanente | Permiso denegado | Fallar o escalar; nunca retry ciego |
| Bug | Forma imposible o invariante rota | Detener, alertar y conservar evidencia |

El executor devuelve códigos tipados. El modelo no debe inferir retryability desde una frase humana.

## 2. Retry no es replanning

- **Retry:** misma intención, mismos argumentos e identidad del efecto.
- **Repair:** corrige una entrada inválida dentro de un límite pequeño.
- **Replan:** cambia estrategia porque el estado del mundo cambió.
- **Reflect:** evalúa evidencia y propone otra decisión.
- **Escalate:** solicita autoridad o juicio que el sistema no posee.

Contabilízalos por separado. Un agente que «razona» diez veces sobre un 403 solo está ocultando un
retry defectuoso.

## 3. Idempotency key

Deriva una identidad estable de la intención, no del número de intento:

```text
effect_key = hash(tenant, task_id, effect_type, canonical_arguments, policy_version)
```

El sistema receptor ideal acepta esa key y devuelve el mismo receipt. Si no la soporta, crea una
tabla local de intents y reconcilia mediante un identificador de negocio antes de repetir.

Idempotencia no significa «ejecutar dos veces es barato». Significa que reintentar la misma intención
produce un único efecto observable.

## 4. La ventana de ambigüedad

Secuencia peligrosa:

1. persistes intent `pending`;
2. envías la acción externa;
3. el proveedor la acepta;
4. el proceso cae antes de persistir el receipt.

Al reanudar, consulta primero por effect key o identificador de negocio. Solo vuelve a enviar si
puedes demostrar que no existe. Cuando esa demostración no es posible, termina en `needs_human` en
vez de apostar con un efecto irreversible.

## 5. Journal y checkpoint

El journal es append-only y registra eventos aceptados. El checkpoint es una proyección compacta
para reanudar rápido. Conserva ambos:

- el checkpoint responde «¿desde dónde sigo?»;
- el journal responde «¿cómo llegué y qué debo reconciliar?».

Persiste el evento y el estado en una transacción cuando compartan base de datos. Para recursos
externos, conserva intent, effect key, request ID y receipt.

## 6. Compatibilidad de versión

Un checkpoint contiene versión de schema, loop, policy y capabilities. Al desplegar una versión
nueva, decide explícitamente:

- reanudar sin cambio;
- migrar estado con función probada;
- mantener el worker antiguo hasta drenar runs;
- cancelar y crear una tarea nueva.

Nunca deserialices estado antiguo y asumas defaults silenciosos para permisos o efectos.

## 7. Cancelación segura

Cancelar impide admitir nuevos pasos, pero no deshace mágicamente un efecto en curso. Marca la
solicitud, espera o interrumpe según la capability y reconcilia el resultado. Si existe compensación,
es otra acción con su propia identidad, permisos y posibles fallos.

`cancelled` debe conservar qué quedó completado, qué sigue incierto y qué limpieza se programó.

## 8. Test que importa

Inyecta el crash entre aceptación externa y persistencia local. Reanuda desde el último checkpoint y
demuestra mediante receipts que el efecto existe exactamente una vez. Un test que falla solo antes
de llamar a la tool no cubre el problema real.
