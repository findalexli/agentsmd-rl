# Enable concurrent dev instances across multiple repo clones

## Problem

When running the Tuist server (`server/`) and cache service (`cache/`) locally from multiple cloned copies of the repo, all instances collide on the same hardcoded ports and database names:

- The server always binds to port `8080`
- The cache service uses port `8087` (and the old README incorrectly says `4000`)
- MinIO uses ports `9095` and `9098`
- PostgreSQL and ClickHouse databases are always named `tuist_development` / `tuist_test`

This makes it impossible to run two independent local environments side by side — for example, when working on separate branches or when multiple agents need their own isolated dev stacks.

## Expected Behavior

Each repo clone should be able to run its own isolated set of services with unique ports and database names, without conflicting with other clones. A persistent per-clone numeric suffix (stored in a file) should be used to derive all configurable values (ports, DB names, etc.) from a single source of truth.

Both the server and cache services need to read these values from the environment. The `mise` tool configuration should source a shared script that sets up the environment automatically.

## Files to Look At

- `mise/utilities/` — this is where shared mise shell scripts live; you'll need to create the env setup script here
- `server/config/runtime.exs` — server runtime configuration; currently hardcodes port `8080`
- `server/lib/tuist/environment.ex` — environment helpers; hardcodes MinIO ports and app URL
- `cache/config/runtime.exs` — cache runtime configuration; needs dev-mode port/URL override
- `server/config/test.exs` and `cache/config/test.exs` — test configs with hardcoded ports and DB names
- `mise.toml`, `server/mise.toml`, `cache/mise.toml` — mise configs that should source the new env script
- `.gitignore` — the instance state file should not be committed

After implementing the code changes, update the relevant documentation (`server/README.md`, `cache/README.md`) to reflect the new clone-local development setup. The READMEs currently tell developers to open hardcoded URLs like `http://localhost:8080` — this is no longer accurate when instance scoping is enabled.
