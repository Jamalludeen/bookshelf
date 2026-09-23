#!/usr/bin/env bash
# Quick run helper
set -euo pipefail
HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8000}"
LOG_LEVEL="${LOG_LEVEL:-info}"
echo "Starting TaskMaster API on http://${HOST}:${PORT}"
exec uvicorn app.main:app --reload --host "${HOST}" --port "${PORT}" --log-level "${LOG_LEVEL}"
