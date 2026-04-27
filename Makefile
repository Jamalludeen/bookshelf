.PHONY: run

run:
	# Use uvicorn reload mode for local development convenience.
	uvicorn app.main:app --reload --port 8000

# Use `make run` for a one-command local dev server.
# Add more targets here (lint/test) as the project grows.
# Keep target names short and obvious.
# This target assumes dependencies are already installed.
