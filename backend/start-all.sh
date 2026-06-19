#!/usr/bin/env bash
set -euo pipefail

BACKEND_ROOT="$(cd "$(dirname "$0")" && pwd)"
PYTHON="${PYTHON:-python}"
PORT="${PORT:-8000}"

start_service() {
  local name="$1"
  local dir="$2"
  local port="$3"
  echo "Iniciando ${name} en puerto ${port}..."
  (
    cd "${BACKEND_ROOT}/${dir}"
    exec "${PYTHON}" -m uvicorn app.main:app --host 127.0.0.1 --port "${port}"
  ) &
}

start_service "auth-service" "services/auth_service" 8001
start_service "credit-service" "services/credit_service" 8002
start_service "payment-service" "services/payment_service" 8003
start_service "portal-service" "services/portal_service" 8004

echo "Esperando microservicios..."
sleep 4

echo "Iniciando api-gateway en puerto ${PORT}..."
cd "${BACKEND_ROOT}/gateway"
exec "${PYTHON}" -m uvicorn app.main:app --host 0.0.0.0 --port "${PORT}"
