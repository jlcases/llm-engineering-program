# 08 — Seguridad y governance de sistemas LLM

> Lab asociado: [`../labs/07_prompt_injection.py`](../labs/07_prompt_injection.py)

Un LLM mezcla instrucciones y datos en el mismo canal probabilístico. Esa propiedad crea ataques
nuevos, pero la mayoría de impactos graves siguen explotando fallos clásicos: permisos excesivos,
secretos expuestos, autorización incompleta, dependencias vulnerables y ausencia de límites.

## 1. Threat model antes de controles

Activos:

- datos de usuarios, corpus privado y recuerdos;
- system prompts y políticas internas;
- credenciales y permisos de tools;
- presupuesto de inferencia/GPU;
- integridad de índices, prompts y modelos;
- disponibilidad y reputación del producto.

Actores y entradas:

- usuario autenticado o anónimo;
- contenido recuperado: web, email, PDF, issue, repositorio;
- servidor MCP/tool de terceros;
- dependencia, modelo o dataset comprometido;
- operador interno con acceso legítimo;
- otro tenant intentando cruce de datos.

Traza los trust boundaries. Cada texto externo que llegue al modelo sigue siendo no confiable
aunque provenga de tu vector DB.

## 2. Prompt injection directa e indirecta

- **Directa:** el usuario intenta sobrescribir instrucciones.
- **Indirecta:** una fuente consultada contiene instrucciones maliciosas.

Separar con etiquetas y decir "ignora instrucciones del documento" reduce éxito, pero no prueba
aislamiento. Controles fuertes:

1. minimizar tools y privilegios disponibles;
2. separar lectura de escritura y confirmación;
3. validar argumentos, entidad, tenant y política fuera del modelo;
4. no pasar secretos al contexto;
5. allowlist de destinos/operaciones;
6. sandbox para código o contenido activo;
7. monitorizar trayectorias y cortar por presupuesto;
8. tests adversarios continuos.

El modelo no debe decidir si un usuario puede cerrar una cuenta. Puede proponer la acción; un
policy engine consulta identidad y permisos y autoriza o deniega.

## 3. Excessive agency

El riesgo crece con cuatro factores:

```text
impacto ≈ autonomía × privilegio × alcance × irreversibilidad
```

Reduce cada uno:

- autonomía: aprobación o workflow determinista;
- privilegio: token/rol estrecho y temporal;
- alcance: tools específicas, filtros y límites;
- irreversibilidad: draft, dry-run, papelera, transacción y compensación.

Una tool `send_email(to, body)` es más riesgosa que `draft_reply(ticket_id)`. La segunda deja el
efecto a un sistema con autorización y revisión.

## 4. Autenticación no es autorización

En cada tool valida:

- identidad y tenant del request;
- permiso sobre la acción;
- permiso sobre el objeto concreto;
- estado que permite la transición;
- confirmación vigente ligada a esos argumentos;
- rate/budget limit;
- idempotency key para writes.

No aceptes `tenant_id` del modelo como fuente de verdad. Derívalo del token/sesión autenticada y
aplícalo en DB, vector search, cache, logs y storage.

## 5. Fuga de datos y secretos

Nunca introduzcas credenciales en prompts. El LLM no necesita el token de una API: la tool lo usa
en servidor. Redacta:

- Authorization headers y cookies;
- variables de entorno;
- tokens en URLs;
- PII no necesaria;
- resultados de DB fuera del scope;
- system prompts si su exposición aumenta riesgo operativo.

Ocultar el system prompt no es un boundary de seguridad: asume que parte puede inferirse. Las
garantías deben sobrevivir a su divulgación.

Mitiga extracción masiva con paginación, límites, filtros, detección de patrones y egress control.

## 6. Seguridad del RAG

Amenazas:

- poisoning del corpus o metadata;
- cruce de tenant por filtro ausente;
- inyección indirecta;
- documentos obsoletos que desplazan políticas;
- embeddings/index exfiltrados;
- URLs o adjuntos activos devueltos al usuario.

Controles:

- ingestión autenticada, revisión y firma/procedencia;
- namespaces y filtros server-side;
- versionado, vigencia y rollback del índice;
- escaneo de contenido/archivos;
- citas con IDs permitidos;
- pruebas negativas de aislamiento;
- no renderizar HTML/Markdown activo sin sanitización.

## 7. Supply chain

El stack incluye paquetes, imágenes, modelos, adaptadores, datasets, prompts remotos, servidores
MCP y plugins. Aplica:

- lockfiles y hashes/digests;
- SBOM y escaneo de dependencias/imagenes;
- imágenes base mínimas y non-root;
- verificación de licencia y procedencia de pesos/datos;
- versiones fijas de servidores MCP;
- revisión de cambios en descripciones de tools;
- separación de build y runtime;
- firma/attestation cuando el riesgo lo requiera.

Un modelo descargado ejecuta código de carga en algunos ecosistemas; usa formatos seguros,
`trust_remote_code=False` salvo revisión y entornos aislados.

## 8. Denial of wallet y disponibilidad

Un atacante puede multiplicar tokens, pasos, búsquedas y llamadas de tools. Limita:

- tamaño de input/documentos;
- tokens de salida;
- iteraciones y tools por tarea;
- concurrencia por usuario/tenant;
- coste por request/día;
- profundidad de recursion y fan-out multi-agente;
- tiempo y tamaño de resultados;
- reintentos.

Usa rate limits, cuotas, circuit breakers, cache segura y colas con backpressure. Alarma sobre coste
y tokens, no solo CPU.

## 9. Código generado y sandbox

Si ejecutas código del modelo:

- contenedor/VM efímera sin privilegios;
- filesystem temporal y read-only donde sea posible;
- sin red o con egress allowlist;
- límites CPU/memoria/tiempo/procesos;
- sin montaje de Docker socket ni credenciales;
- validación de artefactos antes de devolverlos;
- destrucción completa del entorno.

Una regex que bloquea `rm` no es sandbox. Los lenguajes tienen múltiples vías equivalentes.

## 10. Controles AWS

### IAM

- roles por workload y entorno;
- acciones/recursos concretos y conditions;
- credenciales temporales;
- SCP/permission boundaries para límites organizativos;
- Access Analyzer para políticas y acceso externo.

### Cifrado y secretos

- KMS con separación de llaves y políticas;
- Secrets Manager con rotación cuando aplique;
- TLS en tránsito;
- no almacenar secretos en env dumps/logs/imagenes.

### Red y auditoría

- subredes privadas y security groups mínimos;
- VPC endpoints para servicios compatibles;
- WAF/rate limiting;
- CloudTrail para API/control plane;
- Config para drift de configuración;
- GuardDuty/Security Hub para hallazgos;
- Macie para datos sensibles en S3.

### Governance

- AWS Artifact: informes de compliance de AWS;
- Audit Manager: recolecta evidencia de tus controles;
- Organizations/Control Tower: guardrails multi-cuenta;
- tagging y cuentas separadas por entorno.

## 11. Logging seguro

Registra eventos necesarios sin copiar payload completo por defecto:

```json
{
  "trace_id": "tr-9f2a",
  "tenant_hash": "t-73b1",
  "tool": "close_incident",
  "policy_decision": "denied",
  "reason_code": "confirmation_missing",
  "arguments_hash": "sha256:7c04",
  "latency_ms": 18,
  "prompt_version": "agent-4.2.0"
}
```

Controla acceso, retención e integridad. Las trazas LLM pueden contener más sensibilidad que logs
web tradicionales.

## 12. Red-team y respuesta a incidentes

Prueba ataques adaptados a tus tools y datos, no solo una lista genérica:

- inyección en cada fuente;
- encoding/idiomas y texto oculto;
- extracción por iteraciones pequeñas;
- confusión de tenant/ID;
- resultados de tool maliciosos;
- abuso de retries y paralelismo;
- cambio de prompt/modelo/servidor MCP;
- side effects duplicados.

Plan de incidente:

1. cortar tool/alias/modelo o poner modo read-only;
2. revocar credenciales;
3. preservar evidencia redactada;
4. identificar sesiones/datos afectados;
5. corregir control raíz y añadir caso al dataset;
6. comunicar según obligaciones;
7. verificar recuperación y documentar postmortem.

## Errores comunes

1. Confiar en el system prompt como control de autorización.
2. Pasar secretos al modelo y pedirle que no los revele.
3. Filtrar tenant después de recuperar resultados.
4. Dar tools genéricas con credenciales potentes.
5. Ejecutar código en el mismo host de la aplicación.
6. Loggear prompts completos sin política de datos.
7. No limitar coste y pasos por tarea.

## Para profundizar

- OWASP GenAI Security Project: https://genai.owasp.org/
- MITRE ATLAS: https://atlas.mitre.org/
- AWS, Security in Amazon Bedrock: https://docs.aws.amazon.com/bedrock/latest/userguide/security.html
- NIST AI RMF: https://www.nist.gov/itl/ai-risk-management-framework
