#!/usr/bin/env bash
set -euo pipefail

HOST="${1:-}"
shift || true

if [[ -z "${HOST}" || "$#" -eq 0 ]]; then
  echo "用法: $0 <server_ip> <port1> <port2> ..."
  exit 1
fi

for p in "$@"; do
  if timeout 1 bash -c ">/dev/tcp/${HOST}/${p}" 2>/dev/null; then
    echo "OPEN     ${p}"
  else
    echo "FILTERED ${p}"
  fi
done