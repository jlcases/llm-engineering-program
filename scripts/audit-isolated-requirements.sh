#!/usr/bin/env bash
set -euo pipefail

audit_root=$(mktemp -d "${TMPDIR:-/tmp}/llmec-isolated-audit.XXXXXX")
cleanup() {
  rm -rf "${audit_root:?}"
}
trap cleanup EXIT

compile_lock() {
  local source=$1
  local target=$2
  uv pip compile "$source" \
    --generate-hashes \
    --universal \
    --python-version 3.12 \
    --output-file "$target" >/dev/null
}

compile_lock setup/requirements-instructor.txt "$audit_root/instructor.txt"
uv run pip-audit \
  --strict \
  --progress-spinner off \
  --cache-dir "$audit_root/cache" \
  --requirement "$audit_root/instructor.txt" \
  --disable-pip \
  --require-hashes

compile_lock setup/requirements-ragas.txt "$audit_root/ragas.txt"
# GHSA-95ww-475f-pr4f is confined to RAGAS MultiModalFaithfulness URL/file
# processing. GHSA-w8v5-vhqr-4h9v requires loading an attacker-controlled
# DiskCache pickle. The local lab imports only four text metrics, never imports
# DiskCache, and a regression test keeps both vulnerable paths unreachable.
uv run pip-audit \
  --strict \
  --progress-spinner off \
  --cache-dir "$audit_root/cache" \
  --requirement "$audit_root/ragas.txt" \
  --disable-pip \
  --require-hashes \
  --ignore-vuln GHSA-95ww-475f-pr4f \
  --ignore-vuln GHSA-w8v5-vhqr-4h9v
