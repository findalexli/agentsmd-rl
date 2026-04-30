# chore: Remove MaxLineLength suppression guidance from testing skill

Source: [bitwarden/android#6813](https://github.com/bitwarden/android/pull/6813)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/testing-android-code/SKILL.md`

## What to add / change

## 🎟️ Tracking

No ticket — repo tooling cleanup for the `.claude/` Claude Code skill files.

## 📔 Objective

The `testing-android-code` skill contained a prominent STOP block instructing agents when to add `@Suppress(\"MaxLineLength\")`. In practice this primed agents to reach for the annotation reflexively even on lines well under the 100-char limit.

Detekt already runs as a pre-commit hook and flags any line that genuinely exceeds the limit, so in-skill guidance about the suppression is redundant and net-harmful. Removing the block lets detekt serve as the single source of truth.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
