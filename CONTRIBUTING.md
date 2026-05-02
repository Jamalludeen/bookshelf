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

Prefer one topic per commit to simplify review and rollback.

Keep review comments short and concrete when suggesting changes.

Small commits with descriptive messages are strongly preferred.

Include a short reproduction note when opening bug issues.

Add labels like `bug` or `enhancement` to keep triage organized.

Link to the relevant endpoint or file when reporting a bug.

Include expected vs actual behavior in bug reports when possible.
