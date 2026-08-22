# Checklist final del capstone

Marca un elemento solo cuando exista la evidencia enlazada. “Implementado” sin comando, resultado,
URL, trace o artefacto no está terminado. Registra commit y digest de la versión defendida.

## Gates eliminatorios

- [ ] URL HTTPS pública funciona desde una sesión limpia y tiene frontend utilizable.
- [ ] RAGAS faithfulness ≥ 0,75 en dataset final versionado y auditado.
- [ ] Al menos tres tools ejecutan happy path y error con trazas resolubles.
- [ ] Ninguna tool prohibida ni secreto/canario filtrado en la suite adversarial.
- [ ] Tests, build y eval offline pasan sobre el commit/digest de entrega.

## 1. Arquitectura

- [ ] Documento final con contexto, alcance negativo y requisitos RF/RNF medibles.
- [ ] Diagramas de contexto, contenedores y secuencia coinciden con lo desplegado.
- [ ] Al menos cinco ADRs: modelo/routing, vector DB, chunking, agente y cloud.
- [ ] Alternativas y trade-offs incluyen resultados o costes, no solo opiniones.
- [ ] Threat model con activos, trust boundaries, amenazas, controles, owners y tests.
- [ ] Cambios frente a arquitectura v1 explicados.

Evidencia: documento versionado, ADRs aceptados/reemplazados y diagrama exportado.

## 2. RAG

- [ ] Manifest del corpus con licencia/origen, hashes y versiones de parser/chunker/embedding.
- [ ] Ingesta incremental idempotente cubre alta, modificación y baja.
- [ ] Dataset final ≥ 50 preguntas, con negativas, paráfrasis y multi-fuente; test congelado.
- [ ] Retrieval reporta recall/MRR/nDCG por tag y latencia.
- [ ] Generación usa contexto delimitado, citas resolubles y abstención.
- [ ] RAGAS guarda configuración, detalle por caso, coste y audit de peores resultados.
- [ ] Una ablation justifica chunking, híbrida o reranker.
- [ ] Cinco fallos con causa raíz y acción priorizada.

Evidencia: dataset/hash, manifest, resultados JSON, reporte y comando reproducible.

## 3. Agente

- [ ] Grafo/flujo con estado tipado, límite de pasos, timeout y salida degradada.
- [ ] Tres tools no triviales con schemas estrechos, permisos mínimos y errores estructurados.
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
- [ ] Uptime externo ≥ 99 % durante ≥ 14 días, con incidentes explicados.
- [ ] Carga pública versionada: dos corridas, queries variadas, p50/p95/p99, TTFT y errores.
- [ ] P95 cumple el objetivo definido antes de medir.

Evidencia: URL, monitor exportado, workflow/run, digest, scan/SBOM y reportes de carga.

## 5. LLMOps

- [ ] Trace IDs unen API, grafo, tools, retrieval y llamadas de modelo.
- [ ] Dashboard cubre fiabilidad, latencia, calidad/safety, uso/coste.
- [ ] Labels tienen cardinalidad acotada y la redacción pasa el test de canarios.
- [ ] SLI/SLO/error budget están definidos con ventana y exclusiones.
- [ ] Alertas de burn rate, p95, proveedor, coste, calidad y seguridad tienen owner/runbook.
- [ ] Tres alertas fueron provocadas en staging y recuperadas.
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

## 7–8. Certificaciones

- [ ] Simulacro AIF-C01 de 65 preguntas completado; errores clasificados y repasados.
- [ ] NCA-GENL: cinco áreas ponderadas y diez temas repasados; flashcards y simulacro completados.
- [ ] Resultados fechados y plan de repaso de las tres áreas más débiles.

## 9. Demo y defensa

- [ ] Guion de 20 minutos ensayado dos veces por debajo de 19 minutos.
- [ ] Happy path, abstención, ataque/error, aprobación, eval, operación y coste visibles.
- [ ] Plan de contingencia reciente y modo offline; se distingue live de grabado.
- [ ] 42 preguntas revisadas con respuestas basadas en datos propios.
- [ ] Perfil limpio, zoom, red alternativa, estado restablecido y notificaciones silenciadas.
- [ ] Feature freeze; commit, imagen, prompt, modelos y corpus exactos anotados.

## Reproducibilidad por tercero

- [ ] README parte de checkout limpio y llega a tests + ejecución en < 30 minutos.
- [ ] `.env.example` documenta variables sin valores secretos.
- [ ] Locks presentes para Python/Node/infra y versiones actuales verificadas.
- [ ] Licencias de corpus/modelos/dependencias revisadas.
- [ ] Comandos de backup/restore/rollback probados y runbooks accesibles.

## Acta de entrega

Registra en el README final: fecha/hora UTC, commit, digest de imagen, URL, prompt version, corpus
hash, modelos/snapshots, dataset hash, resultados de gates y ubicación de evidencias. Firma la
decisión `go`, `conditional go` o `no-go` con los riesgos aceptados y su owner.
