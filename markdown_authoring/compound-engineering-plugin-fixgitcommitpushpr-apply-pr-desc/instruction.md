# fix(git-commit-push-pr): apply PR description after delegate hand-off

Source: [EveryInc/compound-engineering-plugin#594](https://github.com/EveryInc/compound-engineering-plugin/pull/594)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md`

## What to add / change

Fix a bug where `git-commit-push-pr` would generate a new PR description via `ce-pr-description` and then stop without applying it. Root cause: the apply step was phrased as a subordinate clause ("run step 6, then apply...") after the delegate's `=== TITLE ===` / `=== BODY_FILE ===` return block, and that return block reads as a natural stopping cue.

Promote "apply" to a first-class numbered sub-step with an explicit hand-off-boundary preamble at all three apply sites: Step 7 existing-PR, Step 7 new-PR, and DU-3 description-update. Also align placeholder tokens with `ce-pr-description`'s actual return labels (`<TITLE>` / `<BODY_FILE>`, previously `<returned title>` / `<returned body_file>`) and note the shell-escape hazard for titles containing `"`, `` ` ``, `$`, or `\`.

---

[![Compound Engineering](https://img.shields.io/badge/Built_with-Compound_Engineering-6366f1)](https://github.com/EveryInc/compound-engineering-plugin)
![Claude Code](https://img.shields.io/badge/Opus_4.7_(1M)-D97757?logo=claude&logoColor=white)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
