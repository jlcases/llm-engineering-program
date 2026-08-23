# Ejercicios — Harness Engineering

Estos ejercicios evalúan fronteras y evidencia. No se acepta como prueba una captura del texto final
sin la traza y el estado del entorno.

## 1. Manifiesto mínimo de capacidades

Define tres capabilities para un agente que revisa repositorios: lectura, ejecución de tests y
creación de un comentario de revisión. Incluye schema, efecto, permisos, timeout y errores.

**Criterios de aceptación:**

- el manifest es JSON validable y tiene versión;
- una tarea de solo lectura no descubre la capability de comentario;
- argumentos adicionales se rechazan;
- cada error declara si es retryable;
- un test demuestra que renombrar una capability rompe el contrato de forma visible.

## 2. Path traversal y symlinks

Amplía el lab 01 para permitir una subcarpeta de artefactos y rechazar cualquier escape, incluido un
symlink creado dentro del workspace que apunta fuera.

**Casos obligatorios:**

1. path relativo permitido;
2. `../` rechazado;
3. path absoluto rechazado;
4. symlink hacia fuera rechazado;
5. symlink interno permitido solo si la política lo declara.

## 3. Approval token de un solo uso

Implementa aprobación para una tool con efecto externo. La aprobación debe vincular run, capability,
hash de argumentos y expiración.

**Criterios de aceptación:**

- cambiar un argumento invalida el token;
- reutilizarlo falla;
- un token expirado no llama al executor;
- el log conserva ID y decisión, nunca el token;
- cancelar el run invalida aprobaciones pendientes.

## 4. Redacción estructural

Crea una política que redacte secretos por nombre de campo y tipos sensibles, incluso dentro de
listas anidadas. No alteres datos inocuos que contienen la palabra `token` en texto libre.

Entrega un corpus con positivos y negativos y mide falsos positivos y falsos negativos. Explica qué
datos prohíbes por completo en vez de intentar redactarlos.

## 5. Contaminación entre trials

Introduce deliberadamente una cache compartida que haga pasar el segundo trial. Escribe un test que
detecte la inflación y corrige el runner con namespaces o limpieza.

**La evidencia debe incluir:**

- resultado contaminado;
- causa observable;
- resultado aislado;
- coste adicional del aislamiento;
- decisión sobre qué caches pueden compartirse de forma segura.

## 6. Graders en desacuerdo

Evalúa diez outputs con una regla determinista, un model judge y una pequeña rúbrica humana. No
busques forzar acuerdo: localiza qué dimensión interpreta distinto cada grader.

Reporta matriz de desacuerdo, tres muestras y una política de adjudicación. El resultado final debe
conservar cada señal, no solo una media ponderada.

## 7. Fallo del harness

Haz que el fixture falle antes de iniciar el agente. El sistema debe distinguir `infra_error` de
`agent_failure`, excluirlo del denominador de capacidad y mantenerlo visible en fiabilidad del
harness.

Añade timeout, excepción del grader y fallo de cleanup como rutas adicionales.

## 8. ADR de autoridad

Escribe un ADR comparando:

- todas las tools siempre visibles;
- descubrimiento progresivo;
- selección determinista por tipo de tarea.

Decide con datos de tokens, tasa de selección correcta, latencia y superficie de autoridad. Incluye
la condición que te haría cambiar de alternativa.

## 9. Auditoría de un harness actual

Elige un runtime que no esté en el catálogo y prepara una contribución. No copies su lista de
features: localiza el loop, el assembly de contexto, el protocolo de interacción, la persistencia y
el punto exacto donde se aplican permisos.

**Criterios de aceptación:**

- repo y documentación primaria con fecha de revisión;
- capa y cohorte defendidas con evidencia;
- hechos separados de hipótesis de benchmark;
- trust boundary que incluye instalación, credenciales, red y estado persistente;
- test que falla si el ID, repositorio o fuente se duplica;
- ninguna métrica de popularidad usada como evidencia de calidad.

## 10. Pregunta inválida

Amplía el lab 03 con una comparación solicitada por una persona de producto que mezcle un ADE y un
coding runtime. El programa debe rechazar causalidad directa y proponer dos diseños alternativos:
comparación de runtimes o tratamiento de composición.

Añade tests para cohorte compatible, capa incompatible, controles end-to-end incompletos, seam de
composición desconocido y uno verificado. El mensaje de error debe explicar qué variable impide la
afirmación, no limitarse a `invalid`.

## 11. Mini-edición de benchmark

Convierte una tarea de reparación en una suite de seis fixtures: dos felices, dos con fallo de tool,
uno con presión de contexto y uno con permiso denegado. Ejecuta dos candidatos en orden alterno con
al menos tres repeticiones planificadas.

Entrega resultados trial a trial, outcome rate por familia, fiabilidad del harness, eficiencia
condicionada a éxito, intervalos y todos los errores de infraestructura. Explica qué conclusión no
puedes sostener aunque un candidato quede primero.

## Entrega

Publica código, tests happy/non-happy, un manifest de ejemplo, dos trazas redactadas, un informe de
trials y el ADR. Una persona revisora debe poder reproducir todo sin credenciales de producción.
