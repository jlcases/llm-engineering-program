# Ejercicios — Módulo VIII

Trabaja con SLOs, presupuestos y artefactos reproducibles. “No falló durante mi prueba” no equivale
a disponibilidad; “el promedio bajó” no equivale a una mejora de p95.

## 1. Contrato de observabilidad

Define un esquema de span para un pipeline RAG/agente: trace/span/parent IDs, versión, latencia,
tokens, coste, estado, retry y error. Decide qué datos no registrarás, cómo redactarlos y cuánto se
retienen. Añade un test que falle si aparece un canario secreto en JSONL.

## 2. SLO y alertas

Define SLI/SLO para éxito de tarea, disponibilidad, p95, errores de proveedor y coste. Construye
burn-rate alerts de ventana rápida/lenta. Distingue un 200 con respuesta inútil de un éxito real y
explica qué señal se calcula online y cuál por muestreo.

## 3. Trazas distribuidas

Propaga contexto desde API a retriever, cola y worker. Simula retry y demuestra que mantiene trace
pero crea un span nuevo con vínculo al intento. Evita prompts en baggage/headers. Reconstruye la
critical path de una petición.

## 4. Cache semántico calibrado

Crea 100 pares: equivalentes, cercanos pero distintos y no relacionados. Elige umbral sobre dev y
mide precision/recall en test. Segmenta por tenant/model/prompt/corpus, implementa TTL e invalidación
y calcula hit rate, ahorro, falsos hits y p95.

## 5. Model routing

Evalúa Luna/Terra/Sol —o los tiers actuales cuando ejecutes— sobre 50 tareas reales. Entrena reglas
solo con dev. Reporta calidad, coste y latencia por ruta, overrides de riesgo y regret frente al
modelo mínimo que habría superado el caso. Congela aliases/snapshots usados.

## 6. Batch y concurrencia

Compara 1, 4, 16 y 32 requests concurrentes. Mide TTFT, p50/p95, throughput, errores y rate limits.
Implementa semaphore, timeout y backoff con jitter. Decide un límite de concurrencia a partir de
curvas, no del máximo que no falló una vez.

## 7. Gate de regresión

Amplía el lab 05 a 100 casos con segmentos críticos. El PR ejecuta checks offline; la corrida live
es autorizada, versionada y presupuestada. Bloquea regresiones globales/segmentos y conserva el
artefacto aun cuando falle. Añade un caso que reproduzca un incidente real.

## 8. Imagen y supply chain

Construye el lab Docker multi-arch, genera SBOM, escanea CVEs y firma la imagen. Compara tamaños de
stages. Verifica non-root, filesystem read-only, señales, health y ausencia de `.env`. Documenta el
proceso de actualización de base y rollback por digest.

## 9. Serving local

Elige un modelo instalado desde el catálogo actual de Ollama. Mide warm/cold start, tokens/s y
calidad antes/después de cuantización sobre 30 casos. Después carga concurrente y explica por qué
los resultados locales no prueban que Ollama sea un servidor multi-tenant de producción.

## 10. Threat model LLM

Modela activos, límites de confianza y atacantes para RAG + tools. Cubre injection directa/indirecta,
poisoning, exfiltración, confused deputy, DoS económico y supply chain. Asigna controles preventivos,
detectivos y de recuperación; prueba al menos uno por amenaza crítica.

## 11. Responsible AI y safety

Crea pares contrafactuales y segmentos relevantes para tu aplicación. Evalúa outcome y tasa de
abstención con intervalos. Escribe model/system card con uso previsto, límites y canales de appeal.
Diseña moderación de entrada/salida que no bloquee soporte legítimo sobre abuso.

## 12. Hito — operar el sistema de módulos III/IV

Despliega el RAG o agente construido, primero en staging y después en un destino justificado.

```text
operations/
├── Dockerfile + lock + SBOM
├── deploy/                 # infraestructura/config sin secretos
├── dashboards/             # queries y alertas versionadas
├── eval/                   # gates offline/live
├── runbooks/               # incidentes, rollback, proveedor caído
├── threat-model.md
├── system-card.md
└── cost-report.md
```

Gates:

- imagen non-root, escaneada, fijada por digest y con rollback probado;
- success rate de tarea y p95 bajo SLO durante una prueba de carga declarada;
- timeout, retry, circuit breaker, rate limit y presupuesto por tenant;
- dashboard de calidad, latencia, tokens/coste y errores sin datos sensibles;
- gate de eval que bloquea una regresión simulada;
- alarma comprobada con un fallo inyectado y runbook ejecutado;
- coste real del periodo y proyección a 10× con supuestos.

La evidencia debe incluir timestamps, versiones y resultados; capturas sin configuración no bastan.
