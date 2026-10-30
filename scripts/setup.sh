#!/usr/bin/env bash
set -euo pipefail
FOUNDATION_PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$FOUNDATION_PROJECT_ROOT"
command -v python3 >/dev/null || { echo 'Python 3.11+ is required.' >&2; exit 1; }
command -v npm >/dev/null || { echo 'Node.js and npm are required. See LOCAL_SETUP_AND_WORKFLOW.md.' >&2; exit 1; }
python3 -c 'import sys; assert sys.version_info >= (3,11), "Python 3.11+ required"'
node -e 'const [a,b]=process.versions.node.split(".").map(Number);if(a<18||(a===18&&b<18)){console.error("Node 18.18+ required");process.exit(1)}'
if [[ ! -x .venv/bin/python ]]; then
 if ! python3 -m venv .venv; then
  echo 'Virtual environment creation failed. On Ubuntu install python3-venv; see LOCAL_SETUP_AND_WORKFLOW.md. The parent folder virtualenv is not used.' >&2
  exit 1
 fi
fi
if ! .venv/bin/python -m pip --version >/dev/null 2>&1; then
 echo 'This project virtualenv has no working pip. Recreate only foundation-mvp/.venv after installing venv support; see the guide.' >&2
 exit 1
fi
.venv/bin/python -m pip install -r backend/requirements.txt
if [[ -f frontend/package-lock.json ]]; then
 (cd frontend && npm ci)
else
 (cd frontend && npm install)
fi
if [[ ! -f frontend/.env.local ]]; then cp frontend/.env.example frontend/.env.local; fi
.venv/bin/python scripts/check_environment.py
echo 'Setup finished. Start with: bash scripts/start-local.sh'
