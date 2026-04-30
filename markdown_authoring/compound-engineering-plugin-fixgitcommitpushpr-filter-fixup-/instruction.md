# fix(git-commit-push-pr): filter fix-up commits from PR descriptions

Source: [EveryInc/compound-engineering-plugin#484](https://github.com/EveryInc/compound-engineering-plugin/pull/484)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md`

## What to add / change

PR descriptions were surfacing code review fixes, lint fixes, and other iteration work-product as if they were distinct features of the change. When updating an existing PR description after pushing review fixes, this was especially noticeable — the model would add a "Review feedback addressed" section or elevate fix-up commits to feature bullets.

The root cause: the skill gathered all commits via `git log`, then tried to describe all of them. The existing "Describe the net result, not the journey" writing principle was correct but too far downstream — by the time the model reads it, fix-up commits are already framed as "things that happened."

This adds a **commit classification step** that runs *before* writing begins, with reinforcements at the two update entry points:

1. **New "Classify commits before writing" section** (in "Gather the branch scope") — introduces feature vs fix-up classification. Tells the model to mentally subtract fix-up commits when sizing, so a 12-commit branch with 9 fix-ups reads as a 3-commit PR.
2. **DU-3 reinforcement** — calls out that description updates are the most common trigger for this failure mode.
3. **Step 7 existing-PR reinforcement** — same note for the "push then update" flow.

---

[![Compound Engineering](https://img.shields.io/badge/Compound_Engineering-6366f1)](https://github.com/EveryInc/compound-engineering-plugin)
🤖 Generated with Claude Opus 4.6 (1M context, extended thinking) via [Conductor](https://conductor.app)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
