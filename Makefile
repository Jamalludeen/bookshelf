.PHONY: run

run:
	uvicorn app.main:app --reload --port 8000

# Use `make run` for a one-command local dev server.
