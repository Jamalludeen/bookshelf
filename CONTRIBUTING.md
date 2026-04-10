## Quick run (local)

To run the development server locally:

```bash
pip install -r requirements.txt || pip install fastapi uvicorn sqlalchemy passlib[bcrypt]
uvicorn app.main:app --reload --port 8000
```

This file provides a short developer hint for getting started.

Please open an issue or submit a PR if you'd like to contribute changes.

You can run the project locally using `run.sh` for convenience.

Optional: set `DATABASE_URL` to point to a different database backend.

Please keep PRs small and focused when possible.
