# Checklist final del proyecto de campo

Marca un elemento solo cuando exista la evidencia enlazada. “Implementado” sin comando, resultado,
URL, trace o artefacto no está terminado. Registra commit y digest de la versión revisada.

## Gates no negociables

- [ ] El JTBD funciona de extremo a extremo desde una interfaz adecuada para su usuario.
- [ ] Las señales de evidencia cumplen los umbrales predefinidos en un dataset versionado y auditado.
- [ ] Cada capability ejecuta happy path y errores relevantes con trazas resolubles.
- [ ] Ninguna tool prohibida ni secreto/canario filtrado en la suite adversarial.
- [ ] Tests, build y eval offline pasan sobre el commit/digest de entrega.

## 1. Arquitectura

- [ ] Documento final con contexto, alcance negativo y requisitos RF/RNF medibles.
- [ ] Diagramas de contexto, contenedores y secuencia coinciden con lo desplegado.
- [ ] Las decisiones irreversibles o costosas tienen ADR con alternativas y señal de revisión.
- [ ] Alternativas y trade-offs incluyen resultados o costes, no solo opiniones.
- [ ] Threat model con activos, trust boundaries, amenazas, controles, owners y tests.
- [ ] Cambios frente a arquitectura v1 explicados.

Evidencia: documento versionado, ADRs aceptados/reemplazados y diagrama exportado.

## 2. RAG

- [ ] Manifest del corpus con licencia/origen, hashes y versiones de parser/chunker/embedding.
- [ ] Ingesta incremental idempotente cubre alta, modificación y baja.
- [ ] Dataset con cobertura suficiente por segmento, negativas, paráfrasis y casos multi-fuente;
  holdout congelado.
- [ ] Retrieval reporta recall/MRR/nDCG por tag y latencia.
- [ ] Generación usa contexto delimitado, citas resolubles y abstención.
- [ ] El eval harness guarda configuración, detalle por caso, coste y auditoría de peores resultados.
- [ ] Una ablation justifica chunking, híbrida o reranker.
- [ ] Cinco fallos con causa raíz y acción priorizada.

Evidencia: dataset/hash, manifest, resultados JSON, reporte y comando reproducible.

## 3. Agente

- [ ] Grafo/flujo con estado tipado, límite de pasos, timeout y salida degradada.
- [ ] Las capabilities necesarias tienen schemas estrechos, permisos mínimos y errores estructurados.
- [ ] Escrituras usan idempotencia y confirmación ligada a argumentos/actor/TTL.
- [ ] Retry/backoff distingue errores transitorios de permanentes.
- [ ] Checkpointer permite reanudar sin duplicar side effects.
- [ ] Memoria tiene propósito, aislamiento, retención y borrado, o se justifica no tenerla.
- [ ] Evaluación incluye éxito, trayectoria, seguridad, pasos, tokens, coste y p95.
- [ ] Comparación contra pipeline o agente único demuestra que la complejidad compensa.

Evidencia: tests sin red y cuatro trazas: éxito, error, ataque y aprobación/reanudación.

## 4. Despliegue

- [ ] Imagen multi-stage, non-root, sin `.env`/pesos, escaneada y con SBOM.
- [ ] Despliegue por digest, configuración/secrets externos y rollback probado < 5 min.
- [ ] `/health` y `/ready` tienen contratos distintos y no hacen llamadas pagadas.
- [ ] CI ejecuta tests/evals antes de desplegar; un fallo impide promoción.
- [ ] Rate limit, auth, timeout, circuit breaker y presupuesto por usuario/tenant.
- [ ] El SLO de disponibilidad y su ventana están justificados, medidos externamente y acompañados de
  incidentes explicados.
- [ ] Carga pública versionada: dos corridas, queries variadas, p50/p95/p99, TTFT y errores.
- [ ] P95 cumple el objetivo definido antes de medir.

Evidencia: URL, monitor exportado, workflow/run, digest, scan/SBOM y reportes de carga.

## 5. LLMOps

- [ ] Trace IDs unen API, grafo, tools, retrieval y llamadas de modelo.
- [ ] Dashboard cubre fiabilidad, latencia, calidad/safety, uso/coste.
- [ ] Labels tienen cardinalidad acotada y la redacción pasa el test de canarios.
- [ ] SLI/SLO/error budget están definidos con ventana y exclusiones.
- [ ] Alertas de burn rate, p95, proveedor, coste, calidad y seguridad tienen owner/runbook.
- [ ] Los fallos representativos fueron provocados en staging y recuperados mediante sus runbooks.
- [ ] Un incidente/fallo produjo un test o caso nuevo.

Evidencia: dashboard/queries versionados, alertas, notificaciones y timeline.

## 6. Costes

- [ ] Periodo, moneda, tarifas/fecha/fuentes y créditos están separados.
- [ ] Coste real incluye inferencia, embeddings, evals, retries, tools, infra y observabilidad.
- [ ] Coste medio y p95 por tarea exitosa; desglose por ruta/modelo/segmento.
- [ ] Proyección 10×/100× separa variable, fijo y escalonado e incluye estrés.
- [ ] Optimización elegida tiene ahorro y calidad/latencia medidos.
- [ ] Break-even de self-host incluye capacidad ociosa, HA y operación.

Evidencia: factura/usage redactados, export del dashboard y hoja/script de cálculo.

## 7. Demo y revisión

- [ ] Existe una versión breve y otra profunda del guion, ambas ensayadas.
- [ ] Happy path, abstención, ataque/error, aprobación, eval, operación y coste visibles.
- [ ] Plan de contingencia reciente y modo offline; se distingue live de grabado.
- [ ] Las preguntas de revisión tienen respuestas respaldadas por datos propios o un experimento
  explícito pendiente.
- [ ] Perfil limpio, zoom, red alternativa, estado restablecido y notificaciones silenciadas.
- [ ] Feature freeze; commit, imagen, prompt, modelos y corpus exactos anotados.

## Reproducibilidad por tercero

- [ ] README parte de checkout limpio y llega a tests + ejecución en < 30 minutos.
- [ ] `.env.example` documenta variables sin valores secretos.
- [ ] Locks presentes para Python/Node/infra y versiones actuales verificadas.
- [ ] Licencias de corpus/modelos/dependencias revisadas.
- [ ] Comandos de backup/restore/rollback probados y runbooks accesibles.

## Registro de release

Registra en el README final: fecha/hora UTC, commit, digest de imagen, URL, prompt version, corpus
hash, modelos/snapshots, dataset hash, resultados de gates y ubicación de evidencias. Firma la
decisión `go`, `conditional go` o `no-go` con los riesgos aceptados y su owner.
