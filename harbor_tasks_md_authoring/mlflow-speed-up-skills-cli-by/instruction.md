# Speed up skills CLI by scoping `uv run` to the `skills` package

Source: [mlflow/mlflow#22893](https://github.com/mlflow/mlflow/pull/22893)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/README.md`
- `.claude/skills/add-review-comment/SKILL.md`
- `.claude/skills/analyze-ci/SKILL.md`
- `.claude/skills/fetch-diff/SKILL.md`
- `.claude/skills/fetch-unresolved-comments/SKILL.md`

## What to add / change

### Related Issues/PRs

Relates to #

### What changes are proposed in this pull request?

Update the four `SKILL.md` files and `.claude/skills/README.md` to invoke the skills CLI as:

```bash
uv run --package skills skills <command>
```

instead of `uv run skills <command>`.

**Why**: `.claude/skills` is a uv workspace member of the mlflow project (see `pyproject.toml:266-272`). Without `--package`, `uv run` treats the mlflow workspace root as the active project and syncs **all** of mlflow's dependencies into the venv before running anything — that's hundreds of packages, ~1.2 GB, and ~100 seconds cold on a CI runner with `enable-uv-cache: false` (which `review.yml` uses).

With `--package skills`, uv scopes the sync to just the skills package and its three deps (`aiohttp`, `pydantic`, `typing_extensions`) plus their transitives — 15 packages, a few MB.

**Measured impact**:

| | install size | cold start |
|---|---|---|
| `uv run skills …` | ~1.2 GB (full mlflow workspace) | ~100s (observed on CI) |
| `uv run --package skills skills …` | ~few MB (skills + 14 transitive deps) | ~3s |

The biggest win is the `review` workflow, where `fetch-diff` is the first thing Claude calls and currently eats ~100 seconds of cold-sync time per `/review` invocation.

### How is this PR tested?

- [ ] Existing unit/integration tests
- [ ] New unit/integration tests
- [x] Manual tests

Verified locally:

```bash
$ rm -rf .venv
$ time uv run --package skills skills --help
…
real    0m2.991s
$ 

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
