# feat: add review-renovate agent skill

Source: [backnotprop/plannotator#306](https://github.com/backnotprop/plannotator/pull/306)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/review-renovate/SKILL.md`

## What to add / change

## Summary
- Adds a `review-renovate` skill at `.agents/skills/review-renovate/SKILL.md` following the open agent skills standard
- Codifies the supply chain review process for Renovate PRs that update GitHub Actions
- Agent-agnostic — works with Claude Code, Codex, or any agent supporting the spec

## What the skill does
1. Confirms PR author is Renovate bot
2. Extracts all action version changes from the diff
3. Verifies every pinned commit SHA (old and new) against upstream tagged releases via GitHub API
4. Reviews changelogs for breaking changes
5. Checks workflow files for compatibility
6. Reports a clear safe/unsafe merge recommendation

## Test plan
- [ ] Invoke skill against a Renovate PR and verify it produces the expected summary table
- [ ] Confirm SHA verification catches a tampered hash

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
