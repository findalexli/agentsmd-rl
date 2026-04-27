# chore: Align PR checklist with CI workflow

Source: [swc-project/swc#11560](https://github.com/swc-project/swc/pull/11560)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

## Summary\n- add a PR/CI section to AGENTS.md based on .github/workflows/CI.yml\n- document local baseline checks (fmt, clippy, deny, shear, check)\n- document crate-specific and bindings/node test commands to mirror CI\n\n## Why\n- make Codex-generated PRs more likely to pass CI by running the right local checks before opening/updating PRs

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
