# Sync local virtualenv before mypy and freeze the `update-uv-lock` prek hook

This Airflow repository runs mypy on **non-provider projects** (`airflow-core`,
`task-sdk`, `airflow-ctl`, `dev`, `scripts`, `devel-common`) using a local prek
helper script — `scripts/ci/prek/mypy_local_folder.py` — rather than the breeze
Docker image. Two related problems need to be fixed.

## Problem 1 — local mypy results drift from CI

When run locally (i.e. when the `CI` environment variable is **not** set), the
script currently invokes mypy directly inside the project's `uv` virtualenv
without first making sure that virtualenv matches `uv.lock`. The local `.venv`
can drift from `uv.lock` for many reasons (switching branches, installing
extras, an old environment from a previous Airflow version, etc.). When that
happens, mypy picks up a different set of installed packages than CI uses, and
contributors hit type errors locally that don't reproduce in CI — or worse,
miss type errors locally that CI then catches. CI itself uses `uv.lock` as the
authoritative dependency set.

Fix the local branch of the script (the `else:` branch — leave the `if CI:`
branch untouched) so that, **before** any `uv run … mypy …` invocation, it
first synchronizes the project's virtualenv against `uv.lock`. The sync must:

- use `uv`'s `sync` subcommand,
- pass the **same project name** the script already passes to `uv run` (the
  value resolved from the existing `FOLDER_TO_PROJECT` mapping based on the
  first folder argument),
- pass `--frozen` so `uv.lock` itself is **not** rewritten by the sync,
- and run from the same working directory as the existing `uv run` call.

If the sync command fails (non-zero exit), the script must:

- print a clear error message that names the failed sync command and explains
  that the local virtualenv may not match `uv.lock`, then
- exit with the **same non-zero exit code** the sync produced, **without
  invoking mypy** at all.

The CI/breeze branch (selected when `CI` is set) must remain unchanged — the
new sync step is purely a local-developer concern. CI already builds its
environment from `uv.lock` via the breeze image.

The error/help message printed when mypy itself fails should also be updated to
show the new two-step recipe (`uv sync --frozen --project <PROJECT>` followed
by `uv run --frozen --project <PROJECT> --with "apache-airflow-devel-common[mypy]" mypy <files>`).

## Problem 2 — `update-uv-lock` prek hook silently rewrites `uv.lock`

In `.pre-commit-config.yaml`, the prek hook with id `update-uv-lock` currently
runs plain `uv lock` whenever any `pyproject.toml` changes. That command will
silently rewrite `uv.lock` during the commit if it has gone stale, which makes
lock-file changes invisible to reviewers (the hook auto-fixes and the diff
appears as part of the commit but no one explicitly asked for it).

Change the hook so that, instead of rewriting the lock during a commit, it
**verifies** the lock against `pyproject.toml` and **fails the hook** if the
lock would need updating. Use `uv`'s `--frozen` flag to enable this
verification-only mode — the hook's `entry:` field should become
`uv lock --frozen`. With this change, a contributor whose `pyproject.toml`
edit invalidates `uv.lock` is forced to run the lock refresh explicitly and
commit the regenerated `uv.lock`, keeping lock updates intentional and
reviewable.

Update the comment block immediately above the hook so it reflects the new
behavior — describe that the hook runs locally with `--frozen`, that the lock
is only verified (never silently rewritten during a commit), and what the
contributor must do if the hook fails.

## Problem 3 — keep agent and contributor docs in sync

Two documentation files describe how to run mypy locally and must reflect the
new flow:

- `AGENTS.md` — the **Type-check (non-providers)** bullet under `## Commands`
  currently shows only the `uv run … mypy …` step. Update it to describe the
  two-step flow: first `uv sync --frozen --project <PROJECT>` to align the
  local virtualenv with `uv.lock` (the dependency set CI uses), then the
  `uv run --frozen --project <PROJECT> --with "apache-airflow-devel-common[mypy]" mypy path/to/code`
  invocation.
- `contributing-docs/08_static_code_checks.rst` — the section that documents
  running mypy directly for non-provider projects must explain (in prose, with
  a `.. code-block:: bash` example) that contributors should run
  `uv sync --frozen --project <PROJECT>` first to match CI's dependency set,
  then invoke mypy with `--frozen` so `uv` does not update `uv.lock`.

## Acceptance criteria

A correct fix must satisfy **all** of:

1. Running `scripts/ci/prek/mypy_local_folder.py <FOLDER>` with `CI` unset
   invokes `uv sync --frozen --project <PROJECT>` **before** any
   `uv run … mypy …` invocation.
2. The `--project` value passed to `uv sync` equals the `--project` value
   passed to the existing `uv run` call (i.e. the existing folder→project
   mapping is reused).
3. When `uv sync` exits non-zero, the script exits with the same non-zero
   code and does **not** invoke `uv run … mypy …`.
4. The `update-uv-lock` hook in `.pre-commit-config.yaml` has
   `entry: uv lock --frozen`.
5. The script remains valid Python; the YAML file remains valid YAML; the CI
   branch (`if CI:` in the script) still dispatches via
   `run_command_via_breeze_shell`.
6. `AGENTS.md` and `contributing-docs/08_static_code_checks.rst` describe the
   new two-step `uv sync --frozen` → mypy flow.

## Code Style Requirements

- Python files in this repo are formatted and checked with **ruff** —
  `uv run ruff format <file>` and `uv run ruff check --fix <file>` after any
  edit. Keep the existing Apache License header on the script.
- Imports stay at the top of the file; do not add new top-level imports the
  script does not already use (`subprocess`, `os`, `sys` are all imported at
  the top of `mypy_local_folder.py`).
- Match the surrounding code style — the existing `subprocess.run(...)` block
  for the mypy invocation is a good template for the new sync invocation.
