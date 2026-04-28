# Add create-pr and monitor-pr AI agent skills

Source: [BabylonJS/Babylon.js#18338](https://github.com/BabylonJS/Babylon.js/pull/18338)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/skills/create-pr/SKILL.md`
- `.github/skills/monitor-pr/SKILL.md`

## What to add / change

> 🤖 *This PR was created by the create-pr skill.*

Adds two new AI agent skills under `.github/skills/`:

- **create-pr** — Orchestrates the full PR lifecycle: gathers inputs (push remote, upstream remote, base branch, title/body, reviewers, labels), optionally merges upstream, pushes the branch, creates a draft PR, runs a self code review, marks the PR ready for review, then hands off to the monitor loop and iterates on review comments and CI failures. Supports both `automatic` and `interactive` modes, and an `--pr <number>` shortcut to monitor an existing PR.
- **monitor-pr** — Maintains a live status table for one or more PRs (CI checks, resolved/total comments, reviewer approval) and surfaces actionable events for the orchestrator to react to.

Both skills are documentation only (Markdown `SKILL.md` files) and do not change any runtime code or built artifacts.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
