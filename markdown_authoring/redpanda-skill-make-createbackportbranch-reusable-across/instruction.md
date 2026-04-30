# skill: make create-backport-branch reusable across repos

Source: [redpanda-data/redpanda#30248](https://github.com/redpanda-data/redpanda/pull/30248)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/create-backport-branch/SKILL.md`

## What to add / change

## Summary

Two small non-breaking tweaks to `.claude/skills/create-backport-branch/SKILL.md` added in PR #30175 so the skill is easy to invoke from any repo — by humans or workflows — without having to override its body in the prompt.

- Step 3: `gh api repos/{owner}/{repo}/...` instead of the hardcoded `redpanda-data/redpanda`. `gh` auto-resolves the placeholders from the git remote of the current directory ([gh api docs](https://cli.github.com/manual/gh_api)).
- Step 6: source-PR URL derived via `gh pr view --json url`, plus an optional `SKILL_REPORT_FILE` env var for machine-readable handoff. When set, the skill also writes the Final-report text to that path — designed to be usable verbatim as a PR body (promoted "Conflict details" and the generated-files warning to proper H2 headings for nicer rendering).

Humans invoking the skill directly see no behavioural change.

## Why

[DEVPROD-4091] is wiring this skill into the `/backport` workflow as an AI-assisted conflict-resolution fallback. The original prompt from the staging PR was ~30 lines overriding skill internals (where to `cd`, to skip step 3, to write a custom handoff file to `\$GITHUB_ENV`). Pushing the reusable logic into the skill shrinks the workflow prompt to ~10 lines and keeps the skill usable by humans.

## Test plan

- [x] Re-ran all four skill evals (\`clean-cherry-pick\`, \`multi-commit-conflict\`, \`generated-files-modify-delete\`, \`already-present-empty\`) against the patched SKILL.md i

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
