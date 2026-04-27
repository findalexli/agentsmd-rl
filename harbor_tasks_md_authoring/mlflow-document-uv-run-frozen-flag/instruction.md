# Document `uv run --frozen` flag for offline/no-network usage in `CLAUDE.md`

Source: [mlflow/mlflow#22505](https://github.com/mlflow/mlflow/pull/22505)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

`uv run` attempts to resolve dependencies against PyPI on every invocation; without `--frozen`, any `uv run` command fails when PyPI is unreachable. Since `uv.lock` is already committed, `--frozen` is safe to use when the required dependencies are already installed or available in the local cache.

### What changes are proposed in this pull request?

- **`CLAUDE.md`** — Added an "Offline / No-Network Usage" subsection at the top of the "Development Commands" section documenting `--frozen`. The description clarifies that `--frozen` applies to `uv run` commands that should use the existing `uv.lock` as-is without modifying the environment (i.e., not commands using `--with` or `--extra` that intentionally install additional packages):

```bash
uv run --frozen pytest tests/
```

### How is this PR tested?

- [x] Manual tests

### Does this PR require documentation update?

- [x] Yes. I've updated:
  - [x] Instructions

### Does this PR require updating the [MLflow Skills](https://github.com/mlflow/skills) repository?

- [x] No.

### Release Notes

#### Is this a user-facing change?

- [x] Yes. Give a description of this change to be included in the release notes for MLflow users.

Documents the `--frozen` flag for `uv run` in `CLAUDE.md` so developers know how to run commands when PyPI is unreachable, with clarified guidance that it applies when dependencies are already installed or cached and the environment should not be modified.

#### What component(s), interfaces, languages,

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
