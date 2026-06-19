#!/usr/bin/env bash
set -euo pipefail

BACKEND_ROOT="$(cd "$(dirname "$0")" && pwd)"
PYTHON="${PYTHON:-python}"
PORT="${PORT:-8000}"

wait_for_health() {
  local port="$1"
  local name="$2"
  echo "Esperando ${name} en puerto ${port}..."
  "${PYTHON}" - "${port}" "${name}" <<'PY'
import sys
import time
import urllib.error
import urllib.request

port, name = sys.argv[1], sys.argv[2]
url = f"http://127.0.0.1:{port}/health"

for _ in range(45):
    try:
        with urllib.request.urlopen(url, timeout=2) as response:
            if response.status == 200:
                print(f"{name} listo.")
                sys.exit(0)
    except (urllib.error.URLError, TimeoutError):
        pass
    time.sleep(2)

print(f"ERROR: {name} no respondio en el puerto {port}", file=sys.stderr)
sys.exit(1)
PY
}

start_service() {
  local name="$1"
  local dir="$2"
  local port="$3"
  echo "Iniciando ${name} en puerto ${port}..."
  (
    cd "${BACKEND_ROOT}/${dir}"
    exec "${PYTHON}" -m uvicorn app.main:app --host 127.0.0.1 --port "${port}"
  ) &
  wait_for_health "${port}" "${name}"
}

start_service "auth-service" "services/auth_service" 8001
start_service "credit-service" "services/credit_service" 8002
start_service "payment-service" "services/payment_service" 8003
start_service "portal-service" "services/portal_service" 8004

echo "Iniciando api-gateway en puerto ${PORT}..."
cd "${BACKEND_ROOT}/gateway"
exec "${PYTHON}" -m uvicorn app.main:app --host 0.0.0.0 --port "${PORT}"
