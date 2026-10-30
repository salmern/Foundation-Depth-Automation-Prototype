#!/usr/bin/env bash
set -euo pipefail
FOUNDATION_PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$FOUNDATION_PROJECT_ROOT/frontend"
if [[ ! -d node_modules/next ]]; then echo 'Run bash scripts/setup.sh first.' >&2; exit 1; fi
exec npm run dev -- -p "${FOUNDATION_WEB_PORT:-3000}"
