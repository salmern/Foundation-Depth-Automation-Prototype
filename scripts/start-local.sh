#!/usr/bin/env bash
set -euo pipefail
FOUNDATION_PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$FOUNDATION_PROJECT_ROOT"
if [[ ! -x .venv/bin/python || ! -d frontend/node_modules/next ]]; then echo 'Run bash scripts/setup.sh first. Read LOCAL_SETUP_AND_WORKFLOW.md for prerequisites.' >&2; exit 1; fi
if [[ -f .env ]]; then set -a; source .env; set +a; fi
if [[ "${FOUNDATION_API_PORT:-8000}" != 8000 || "${FOUNDATION_WEB_PORT:-3000}" != 3000 ]]; then
 echo 'For custom ports use run-backend.sh and run-frontend.sh in separate terminals; update the API URL and CORS as described in the guide.' >&2
 exit 1
fi
.venv/bin/python - <<'PYPORT'
import socket
for port in (8000,3000):
 with socket.socket() as connection:
  try:connection.bind(('127.0.0.1',port))
  except OSError:raise SystemExit(f'Port {port} is already in use. Stop the old application or use the separate-terminal instructions.')
PYPORT
mkdir -p outputs
FOUNDATION_BACKEND_PID=''
FOUNDATION_FRONTEND_PID=''
cleanup() {
 if [[ -n "$FOUNDATION_FRONTEND_PID" ]]; then kill "$FOUNDATION_FRONTEND_PID" 2>/dev/null || true; fi
 if [[ -n "$FOUNDATION_BACKEND_PID" ]]; then kill "$FOUNDATION_BACKEND_PID" 2>/dev/null || true; fi
}
trap cleanup EXIT INT TERM
bash scripts/run-backend.sh > outputs/local-backend.log 2>&1 &
FOUNDATION_BACKEND_PID=$!
.venv/bin/python - <<'PY'
import time,urllib.request
for attempt in range(30):
 try:
  with urllib.request.urlopen('http://127.0.0.1:8000/api/health',timeout=2) as response:
   if response.status==200:break
 except OSError:time.sleep(1)
else:raise SystemExit('API did not start. Read outputs/local-backend.log and the troubleshooting section of LOCAL_SETUP_AND_WORKFLOW.md.')
PY
bash scripts/run-frontend.sh > outputs/local-frontend.log 2>&1 &
FOUNDATION_FRONTEND_PID=$!
echo 'Frontend starting: http://127.0.0.1:3000'
echo 'API documentation: http://127.0.0.1:8000/docs'
echo 'Logs: outputs/local-backend.log and outputs/local-frontend.log'
echo 'Press Ctrl+C here to stop both services. Initial frontend compilation can take time.'
wait -n "$FOUNDATION_BACKEND_PID" "$FOUNDATION_FRONTEND_PID"
