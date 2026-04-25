# Bug: embedded-postgres initialization fails

## Symptom

When `startEmbeddedDb()` in `packages/cli-module-build/src/lib/runner/startEmbeddedDb.ts` is called, the embedded PostgreSQL database fails to start. The function `pg.initialise()` throws an error.

The `startEmbeddedDb()` function creates a temporary directory for the database, then calls `pg.initialise()` and `pg.start()`. The `cleanStaleDatabases()` function handles stale PID files from previous runs, but the database fails to initialize on first startup.

## Relevant Files

- `packages/cli-module-build/src/lib/runner/startEmbeddedDb.ts` — contains the `startEmbeddedDb()` async function and the `startEmbeddedPostgres()` helper that creates the `EmbeddedPostgres` instance
- The `cleanStaleDatabases()` function already handles stale PID files from prior runs

## What to Look For

The `startEmbeddedDb()` function uses a temporary directory, initializes an `EmbeddedPostgres` instance via `pg.initialise()`, writes a PID file using `fs.writeFile()` with a `PID_FILE` constant, and then starts the database with `pg.start()`. The `PID_FILE` constant is defined at the top of the file and resolves to a `backstage.pid` path. The database directory is created fresh for each startup and is passed to the `EmbeddedPostgres` constructor.

The try block in this function must correctly sequence database initialization and PID file creation so that `pg.initialise()` succeeds.

## What NOT to Do

- Do not add new test files — the existing test suite covers the surrounding logic
- Do not modify any other packages or files
- Do not create changesets — this is a bug fix, not a feature change requiring version bumps
- Do not run builds, installs, or release tooling