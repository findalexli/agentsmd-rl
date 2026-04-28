# Rename CLAUDE.md to AGENTS.md, symlink CLAUDE.md

Source: [grafana/k6#5781](https://github.com/grafana/k6/pull/5781)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`
- `CLAUDE.md`

## What to add / change

## What?

Renames CLAUDE.md to AGENTS.md and adds a CLAUDE.md symlink pointing to it.

## Why?

Part of the k6-core AGENTS.md rollout (grafana/k6#5780). AGENTS.md is vendor-neutral so any coding agent can use it. The CLAUDE.md symlink keeps Claude-based tools working.

## Related PR(s)/Issue(s)

Part of #5780

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
