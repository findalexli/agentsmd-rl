# chore: add severity levels to copilot review instructions

Source: [grafana/tempo#6973](https://github.com/grafana/tempo/pull/6973)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

## Summary

- Adds a `## Severity levels` section to `.github/copilot-instructions.md` defining CRITICAL, HIGH, MEDIUM, and LOW buckets
- Each level includes concrete examples drawn from recent PRs in this repo so Copilot has clear calibration on where the bar sits
- LOW comments are suppressed entirely — Copilot will not leave comments on naming, wording, or minor style issues
- Updates the `## Review style` section to drop the manual "this doesn't block" disclaimer — the severity label now carries that signal

## Test plan

- [ ] Verify Copilot labels its next review comments with CRITICAL/HIGH/MEDIUM
- [ ] Confirm no LOW-severity comments appear

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
