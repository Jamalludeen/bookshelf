#!/usr/bin/env bash
# Quick run helper
set -euo pipefail
echo "Starting TaskMaster API on http://127.0.0.1:8000"
uvicorn app.main:app --reload --port 8000
