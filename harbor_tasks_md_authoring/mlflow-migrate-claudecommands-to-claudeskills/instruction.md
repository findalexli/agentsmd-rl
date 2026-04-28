# Migrate `.claude/commands/` to `.claude/skills/`

Source: [mlflow/mlflow#22539](https://github.com/mlflow/mlflow/pull/22539)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/pr-review/SKILL.md`
- `.claude/skills/resolve/SKILL.md`

## What to add / change

Migrates the two git-tracked custom commands from `.claude/commands/` to the newer `.claude/skills/` format, adding `disable-model-invocation: true` so they are only triggered manually via `/name`.

### Changes

- **`.claude/skills/pr-review/SKILL.md`** — moved from `.claude/commands/pr-review.md`; added `disable-model-invocation: true` to frontmatter
- **`.claude/skills/resolve/SKILL.md`** — moved from `.claude/commands/resolve.md`; added `disable-model-invocation: true` to frontmatter
- **Removed** `.claude/commands/pr-review.md`, `.claude/commands/resolve.md`, and the now-empty `.claude/commands/` directory

### How is this PR tested?

- [x] Manual tests

### Does this PR require documentation update?

- [x] No.

### Does this PR require updating the [MLflow Skills](https://github.com/mlflow/skills) repository?

- [x] No.

### Release Notes

#### Is this a user-facing change?

- [x] No.

#### What component(s), interfaces, languages, and integrations does this PR affect?

Components

- [ ] `area/tracking`: Tracking Service, tracking client APIs, autologging
- [ ] `area/models`: MLmodel format, model serialization/deserialization, flavors
- [ ] `area/model-registry`: Model Registry service, APIs, and the fluent client calls for Model Registry
- [ ] `area/scoring`: MLflow Model server, model deployment tools, Spark UDFs
- [ ] `area/evaluation`: MLflow model evaluation features, evaluation metrics, and evaluation workflows
- [ ] `area/gateway`: MLflow AI Gateway client APIs, 

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
