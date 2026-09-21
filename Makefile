.PHONY: run health info

run:
	# Use uvicorn reload mode for local development convenience.
	uvicorn app.main:app --reload --port 8000

health:
	# Check that the local API process can answer a health request.
	curl --fail --silent http://127.0.0.1:8000/health

info:
	@printf 'Run: make run\nCheck: make health\n'

# Use `make run` for a one-command local dev server.
# Add more targets here (lint/test) as the project grows.
# Keep target names short and obvious.
# This target assumes dependencies are already installed.
# `uvicorn` is launched with reload for fast feedback.
# Edit the port in this file if you need a different local binding.
