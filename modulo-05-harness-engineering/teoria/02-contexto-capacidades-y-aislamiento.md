# 02 — Contexto, capacidades y aislamiento

Un harness no mejora por entregar más tokens. Mejora cuando el agente puede descubrir la pieza de
contexto o la capacidad correcta en el momento correcto, y cuando el sistema impide que esa
capacidad exceda la autoridad de la tarea.

## 1. Legibilidad antes que volumen

Organiza el contexto en capas:

1. **Contrato permanente:** propósito, límites, formato de salida y política de seguridad.
2. **Mapa:** nombres y descripciones breves de dominios, repositorios y capabilities.
3. **Detalle bajo demanda:** archivos, esquemas, logs o métricas solicitados por una decisión.
4. **Estado del run:** plan vigente, artefactos, presupuestos y última observación.
5. **Handoff:** resumen estructurado suficiente para reanudar con una ventana limpia.

El mapa debe permitir elegir sin contener el manual completo. Si cada tool inyecta toda su
documentación en cada turno, el coste sube y las señales relevantes compiten con texto inerte.

## 2. Descubrimiento progresivo

Un manifiesto público puede exponer nombre, descripción, clase de efecto y esquema resumido. El
harness entrega el contrato completo solo cuando la capability entra en el conjunto candidato.

```text
task -> capability classes -> candidate manifests -> selected full contract -> invocation
```

Mide el resultado. El descubrimiento progresivo es peor si aumenta selecciones erróneas o necesita
tantas rondas que supera el ahorro de contexto.

## 3. Autoridad en cuatro puertas

Una llamada sensible debe atravesar cuatro controles independientes:

| Puerta | Pregunta | Control determinista |
|---|---|---|
| Descubrimiento | ¿Debe conocer esta capability? | Filtro por tarea y rol |
| Invocación | ¿Puede llamarla ahora? | Allowlist y estado del run |
| Argumentos | ¿Qué alcance exacto solicita? | Schema, límites y resolución de identidad |
| Efecto | ¿Puede ejecutarse sin una persona? | Política y approval token de un solo uso |

Ocultar una tool no es una frontera de seguridad. La frontera está en el executor, después de
resolver identidad, permisos y alcance con datos del servidor.

## 4. Sandbox y sistema de archivos

Para una tarea sobre código, usa un workspace desechable o un worktree dedicado. El executor:

- rechaza paths absolutos y traversal;
- resuelve symlinks antes de comprobar la raíz;
- limita tamaño, número de ficheros y tiempo de proceso;
- entrega variables de entorno por allowlist;
- separa red, credenciales y filesystem;
- conserva únicamente los artefactos declarados.

Un contenedor reduce superficie, pero no sustituye permisos de aplicación. Un proceso dentro del
contenedor puede seguir borrar todo el volumen montado si el volumen tiene demasiado alcance.

## 5. Aislamiento entre trials

Cada trial comienza desde el mismo fixture inmutable y recibe un directorio, cache y namespace
propios. Nunca permitas que el segundo trial observe:

- artefactos del primero;
- historial Git creado por una ejecución previa;
- cache con respuestas o embeddings del caso;
- puertos, colas o filas de base de datos compartidas sin partición;
- límites de recursos consumidos por otro worker.

La contaminación puede inflar la puntuación o crear fallos correlacionados. En ambos casos deja de
medirse la capacidad que pretendías evaluar.

## 6. Secretos y trazas

No entregues un almacén completo de variables al proceso. Proporciona credenciales efímeras,
acotadas por recurso y acción. Redacta por estructura antes de serializar: ocultar con una expresión
regular después de escribir el log llega tarde.

Registra que existió una credencial y qué permiso representaba, no su valor. Para debugging, conserva
IDs de solicitud y receipts del proveedor que permitan correlacionar sin revelar el secreto.

## 7. Checklist de diseño

- ¿Una task enumera sus capabilities y presupuestos?
- ¿El executor vuelve a comprobar autoridad aunque el modelo haya elegido bien?
- ¿Un path se valida después de resolverlo?
- ¿Cada trial empieza desde un estado limpio demostrable?
- ¿La traza puede compartirse sin credenciales ni datos personales?
- ¿La limpieza se ejecuta también tras timeout, cancelación y crash?

Si una respuesta depende de «el modelo normalmente no hace eso», falta una frontera del harness.
