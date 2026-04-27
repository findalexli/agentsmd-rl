# Document uv run --project for local integrations

Source: [prefecthq/prefect#21625](https://github.com/PrefectHQ/prefect/pull/21625)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

this PR documents the `uv run --project ./src/integrations/<name> ...` pattern in the root `AGENTS.md`.

<details>
<summary>why</summary>

When working from the repo root, `uv run --project ./src/integrations/<name>` is the clean way to target a local integration source tree without relying on `PYTHONPATH`.

</details>

Validation:
- not run; docs-only change

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
