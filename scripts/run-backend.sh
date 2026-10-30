#!/usr/bin/env bash
set -euo pipefail
FOUNDATION_PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$FOUNDATION_PROJECT_ROOT"
if [[ ! -x .venv/bin/python ]]; then echo 'Run bash scripts/setup.sh first.' >&2; exit 1; fi
if [[ -f .env ]]; then set -a; source .env; set +a; fi
exec .venv/bin/python -m uvicorn foundation_mvp.main:app --app-dir backend/src --host 127.0.0.1 --port "${FOUNDATION_API_PORT:-8000}"
