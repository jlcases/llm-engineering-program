# Lab Docker — API LLMOps endurecida y observable

Este lab empaqueta una FastAPI determinista como control operacional. No requiere claves ni llama a
un LLM: así puedes aislar build, health, señales, métricas y seguridad del contenedor antes de sumar
una dependencia externa.

## Qué demuestra

- multi-stage build con `uv 0.12.5` y dependencias fijadas (catálogo del 21-08-2026);
- runtime slim sin compilador, proceso UID/GID 10001 y `CMD` exec;
- health/readiness separados y sin llamadas pagadas;
- filesystem read-only, capabilities eliminadas y `no-new-privileges` en Compose;
- métricas Prometheus sin labels de usuario ni prompt;
- imagen de Prometheus fijada a `v3.14.0` y retención local de 24 horas.

Revalida periódicamente las versiones y digests; un tag fijado reduce drift, pero no sustituye un
scanner ni una política de actualización.

## Ejecutar

Desde este directorio:

```bash
docker compose config --quiet
docker compose build
docker compose up -d --wait
curl -fsS http://127.0.0.1:8000/health
curl -fsS http://127.0.0.1:8000/ready
curl -fsS -X POST http://127.0.0.1:8000/v1/answer \
  -H 'content-type: application/json' \
  -d '{"question":"He expuesto una clave API, ¿qué hago?"}'
curl -fsS http://127.0.0.1:8000/metrics | head
```

Prometheus queda en <http://127.0.0.1:9090>. Consulta:

```promql
sum by (endpoint, status) (rate(llmops_requests_total[1m]))
```

Para detener sin borrar el volumen de métricas:

```bash
docker compose down
```

## Lectura del Dockerfile

1. `uv-bin` fija la herramienta de build.
2. `builder` crea `/opt/venv`; copiar primero `requirements.txt` conserva la cache.
3. `runtime` recibe solo Python, el venv y `app.py`.
4. El usuario no-root no tiene shell ni home escribible.
5. El health check usa la stdlib; no instala `curl` en runtime.
6. Uvicorn es PID 1 y recibe SIGTERM directamente.

## Pruebas de aceptación

```bash
docker compose ps
docker inspect --format '{{.Config.User}} {{.HostConfig.ReadonlyRootfs}}' llmops-docker-api-1
docker compose exec api python -c 'import os; print(os.getuid())'
docker compose exec api sh -c 'touch /app/forbidden'
```

El UID debe ser `10001`, `ReadonlyRootfs` debe ser `true` y el último comando debe fallar. El
nombre generado del contenedor puede variar: `docker compose ps -q api` devuelve su ID si necesitas
un comando portable.

## Evolución hacia una API real

Inyecta claves desde el secret manager del orquestador, añade cliente async con timeout, circuit
breaker y budget, y conserva `/health` libre de proveedores. Nunca añadas prompt o user ID como
label Prometheus: crea cardinalidad sin límite y filtra datos. Las trazas detalladas pertenecen a un
backend de tracing con redacción y retención definida.
