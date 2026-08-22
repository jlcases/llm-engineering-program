# Ejercicios — Módulo IV

Los agentes se evalúan por tareas completadas y trayectorias seguras, no por lo convincente de su
conversación. Conserva trazas con inputs sensibles redactados y prueba siempre el camino de error.

## 1. ReAct con errores recuperables

Amplía el lab 01 con una tool de inventario que pueda devolver timeout, 404 y 429. Define qué
errores se reintentan, cuántas veces y con qué backoff. Crea tests donde el agente termina sin bucle,
no convierte un error en dato y explica qué no pudo verificar.

## 2. Idempotencia y confirmación

Añade una tool `create_refund` simulada. La ejecución requiere confirmación server-side ligada a
usuario, factura, importe y expiración, además de idempotency key. Simula que la respuesta se pierde
después del commit y demuestra que el reintento no duplica el reembolso.

## 3. Grafo frente a pipeline

Implementa la misma tarea como función lineal y como `StateGraph`. Compara líneas, estados posibles,
testabilidad y coste operacional. Elige el pipeline si no necesitas ramas, pausa ni persistencia;
justifica con requisitos, no con preferencia de framework.

## 4. Ciclo con estancamiento

Al lab 03 añade una huella de `(tool, argumentos, resultado)`. Si se repite dos veces sin nueva
evidencia, corta antes de `max_attempts`. Añade estados finales `ready`, `exhausted`, `stalled` y
tests para cada transición.

## 5. Human-in-the-loop

Crea un grafo que interrumpa antes de cualquier escritura. Presenta al aprobador acción, argumentos,
impacto, principal y TTL. Prueba aprobar, rechazar, editar argumentos y reanudar el proceso tras
reiniciar usando un checkpointer persistente.

## 6. Servidor MCP endurecido

Extiende el lab 05 con almacenamiento SQLite, namespaces por tenant y una tool de borrado que exige
versión esperada. Añade límites, logs a stderr y tests del protocolo con un cliente MCP. Demuestra
que un tenant no puede leer IDs de otro.

## 7. Cliente MCP

Escribe un cliente que conecte al servidor por stdio, liste tools/resources, llame `create_note` y
lea el resource resultante. Verifica versión/capabilities durante initialize, maneja desconexión y
cierra el proceso incluso ante excepción.

## 8. Supervisor evaluado

Construye 20 tareas con ruta esperada. Compara supervisor determinista y router LLM en exactitud de
ruta, tareas resueltas, handoffs, tokens y latencia. Penaliza tanto omitir un especialista crítico
como añadir uno innecesario.

## 9. Multi-agente adversarial

Haz que un especialista devuelva una instrucción maliciosa dentro de su informe. El supervisor debe
tratar el informe como dato no confiable, no habilitar tools nuevas y preservar provenance. Añade
un canario secreto y mide exfiltración observable.

## 10. Política de memoria

Define por campo: propósito, consentimiento, namespace, retención, cifrado, acceso y borrado.
Implementa TTL y `forget_user`. Prueba colisión de IDs entre tenants, prompt injection almacenada y
petición de exportación/borrado. No guardes transcripciones completas por comodidad.

## 11. Evaluación de trayectorias

Crea un evaluator determinista que compruebe tools permitidas, orden, argumentos, repeticiones,
confirmaciones y estado final. Añade un judge solo para calidad semántica y calibra sus resultados
contra 30 anotaciones humanas. Reporta éxito, seguridad, pasos, coste y p95.

## 12. Mini-proyecto — agente de investigación auditable

Construye un agente que investigue una pregunta usando al menos tres capacidades: búsqueda en un
corpus permitido, lectura de documentos y cálculo/verificación. Puede usar un único grafo o
especialistas si la evaluación demuestra que compensa.

```text
research-agent/
├── app/                    # grafo, tools, policy y API/CLI
├── mcp_server/             # al menos una capacidad reutilizable
├── eval/
│   ├── dataset.json        # tareas, evidencia y trayectoria esperada
│   ├── evaluate.py
│   └── results.json
├── tests/                  # tools y grafo sin red
├── threat-model.md
└── README.md
```

Gates mínimos:

- ≥ 30 tareas, cinco negativas y cinco adversariales;
- éxito ≥ 85 % y cero tools prohibidas en el test congelado;
- límite de pasos, timeout, presupuesto y salida degradada;
- citas resolubles para toda afirmación factual auditada;
- confirmación humana para cualquier efecto externo;
- memoria aislada y borrable, o justificación explícita para no tenerla;
- comparación contra un pipeline no agéntico.

La entrega no se aprueba si el agente solo funciona en la demo preparada.
