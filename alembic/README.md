Alembic is included as the migration tool requested by the assignment.

After installing dependencies, initialize a migration environment if you want to manage schema changes with Alembic:

```bash
alembic init alembic
```

Then configure `alembic.ini` / `env.py` to use `settings.DATABASE_URL` and `Base.metadata`.

For this beginner training project, `Base.metadata.create_all()` is used on startup so the API can run immediately.
