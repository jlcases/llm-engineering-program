# Docker Lab — Hardened and Observable LLMOps API

This lab packages a deterministic FastAPI application as an operational control. It requires no API keys and does not call an LLM: this allows you to isolate build, health, signals, metrics, and container security before adding an external dependency.

## What it demonstrates

- multi-stage build with `uv 0.12.5` and pinned dependencies (catalog dated 2026-08-21);
- slim runtime without compiler, UID/GID 10001 process, and `CMD` exec;
- separate health/readiness checks with no paid API calls;
- read-only filesystem, dropped capabilities, and `no-new-privileges` in Compose;
- Prometheus metrics without user labels or prompt data;
- Prometheus image pinned to `v3.14.0` and 24-hour local retention.

Periodically revalidate versions and digests; a pinned tag reduces drift, but does not replace a scanner or an update policy.

## Run

From this directory:

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

Prometheus is available at <http://127.0.0.1:9090>. Query:

```promql
sum by (endpoint, status) (rate(llmops_requests_total[1m]))
```

To stop without deleting the metrics volume:

```bash
docker compose down
```

## Reading the Dockerfile

1. `uv-bin` sets the build tool.
2. `builder` creates `/opt/venv`; copying `requirements.txt` first preserves the cache.
3. `runtime` receives only Python, the venv, and `app.py`.
4. The non-root user has no shell or writable home directory.
5. The health check uses the stdlib; it does not install `curl` at runtime.
6. Uvicorn is PID 1 and receives SIGTERM directly.

## Acceptance tests

```bash
docker compose ps
docker inspect --format '{{.Config.User}} {{.HostConfig.ReadonlyRootfs}}' llmops-docker-api-1
docker compose exec api python -c 'import os; print(os.getuid())'
docker compose exec api sh -c 'touch /app/forbidden'
```

The UID must be `10001`, `ReadonlyRootfs` must be `true`, and the last command must fail. The generated container name may vary: `docker compose ps -q api` returns its ID if you need a portable command.

## Evolution towards a real API

Inject keys from the orchestrator's secret manager, add an async client with timeout, circuit breaker, and budget, and keep `/health` provider-free. Never add prompt or user ID as a Prometheus label: this creates unbounded cardinality and leaks data. Detailed traces belong to a tracing backend with defined authoring and retention policies.