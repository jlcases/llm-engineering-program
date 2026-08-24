#!/usr/bin/env bash
set -Eeuo pipefail

repository_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
docker_root="${repository_root}/modulo-08-production-engineering/docker"
run_suffix="${GITHUB_RUN_ID:-local}-${GITHUB_RUN_ATTEMPT:-0}-$$"
container_name="llmec-production-smoke-${run_suffix}"
image_name="llmec-production-smoke:${run_suffix}"

cleanup() {
  docker rm --force "${container_name}" >/dev/null 2>&1 || true
  docker image rm "${image_name}" >/dev/null 2>&1 || true
}
trap cleanup EXIT

docker compose --file "${docker_root}/docker-compose.yml" config --quiet
docker build --tag "${image_name}" "${docker_root}"
docker run \
  --rm \
  --detach \
  --name "${container_name}" \
  --publish 127.0.0.1::8000 \
  --read-only \
  --tmpfs /tmp:size=16m,mode=1777 \
  --cap-drop ALL \
  --security-opt no-new-privileges=true \
  "${image_name}" >/dev/null

container_user="$(docker inspect --format '{{.Config.User}}' "${container_name}")"
read_only_root="$(docker inspect --format '{{.HostConfig.ReadonlyRootfs}}' "${container_name}")"
security_options="$(docker inspect --format '{{json .HostConfig.SecurityOpt}}' "${container_name}")"
dropped_capabilities="$(docker inspect --format '{{json .HostConfig.CapDrop}}' "${container_name}")"
if [[ -z "${container_user}" || "${container_user}" == "0" || "${container_user}" == "root" ]]; then
  echo "El contenedor se ejecuta como root o sin usuario explícito." >&2
  exit 1
fi
if [[ "${read_only_root}" != "true" ]] \
  || [[ "${security_options}" != *'no-new-privileges'* ]] \
  || [[ "${dropped_capabilities}" != *'ALL'* ]]; then
  echo "El runtime no aplica filesystem read-only, no-new-privileges y cap-drop ALL." >&2
  exit 1
fi

health_status="starting"
for _attempt in {1..30}; do
  health_status="$(docker inspect --format '{{.State.Health.Status}}' "${container_name}")"
  if [[ "${health_status}" == "healthy" ]]; then
    break
  fi
  if [[ "${health_status}" == "unhealthy" ]]; then
    docker logs "${container_name}" >&2
    exit 1
  fi
  sleep 1
done
if [[ "${health_status}" != "healthy" ]]; then
  docker logs "${container_name}" >&2
  echo "El contenedor no alcanzó el estado healthy en 30 segundos." >&2
  exit 1
fi

published_address="$(docker port "${container_name}" 8000/tcp)"
published_port="${published_address##*:}"
base_url="http://127.0.0.1:${published_port}"

health_payload="$(curl --fail --silent --show-error "${base_url}/health")"
ready_payload="$(curl --fail --silent --show-error "${base_url}/ready")"
answer_payload="$(curl --fail --silent --show-error \
  --header 'content-type: application/json' \
  --data '{"question":"How should I revoke an exposed token?"}' \
  "${base_url}/v1/answer")"
invalid_status="$(curl --silent --show-error --output /dev/null --write-out '%{http_code}' \
  --header 'content-type: application/json' \
  --data '{"question":"  "}' \
  "${base_url}/v1/answer")"
unknown_status="$(curl --silent --show-error --output /dev/null --write-out '%{http_code}' \
  "${base_url}/a/user-controlled/path")"
metrics_payload="$(curl --fail --silent --show-error "${base_url}/metrics")"

python3 - "${health_payload}" "${ready_payload}" "${answer_payload}" <<'PY'
import json
import sys

health, ready, answer = map(json.loads, sys.argv[1:])
if health != {"status": "ok"}:
    raise SystemExit(f"health inesperado: {health!r}")
if ready.get("status") != "ready" or not ready.get("pipeline"):
    raise SystemExit(f"readiness inesperado: {ready!r}")
if answer.get("category") != "security" or len(answer.get("request_fingerprint", "")) != 16:
    raise SystemExit(f"respuesta inesperada: {answer!r}")
PY

if [[ "${invalid_status}" != "422" || "${unknown_status}" != "404" ]]; then
  echo "Códigos inesperados: invalid=${invalid_status}, unknown=${unknown_status}." >&2
  exit 1
fi
if ! grep --fixed-strings --quiet 'endpoint="/v1/answer",status="422"' <<<"${metrics_payload}"; then
  echo "La métrica del error de validación no usa la plantilla de ruta." >&2
  exit 1
fi
if ! grep --fixed-strings --quiet 'endpoint="__unmatched__",status="404"' <<<"${metrics_payload}"; then
  echo "La ruta desconocida no usa el label acotado." >&2
  exit 1
fi
if grep --fixed-strings --quiet '/a/user-controlled/path' <<<"${metrics_payload}"; then
  echo "Las métricas exponen una ruta controlada por el usuario." >&2
  exit 1
fi

echo "Contenedor de producción verificado: healthy, no-root, read-only y cardinalidad acotada."
