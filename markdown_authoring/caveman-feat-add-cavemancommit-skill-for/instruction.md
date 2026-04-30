# feat: add caveman-commit skill for terse commit messages

Source: [JuliusBrussee/caveman#44](https://github.com/JuliusBrussee/caveman/pull/44)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/caveman-commit/SKILL.md`

## What to add / change

## Summary

Adds `skills/caveman-commit/SKILL.md` — a domain-specific caveman variant that generates Conventional Commits-style messages: terse subject, body only when "why" isn't obvious, no AI attribution, no fluff.

## How it works

Unlike the language variants (caveman, caveman-es, caveman-cn, caveman-pt), this one is domain-specific. It drops the lite/full/ultra intensity model — commits are binary (subject-only vs subject+body), not a spectrum. It keeps the family spine: Rules / Examples / Auto-Clarity / Boundaries.

Forces:
- Conventional Commits prefix (`feat`, `fix`, `refactor`, etc.)
- Imperative mood, ≤50 char subject, no trailing period
- Body only for non-obvious *why*, breaking changes, migrations
- Always include body for breaking/security/migration/revert (auto-clarity)
- Never includes "this commit", "I/we", or AI attribution

## Examples

❌ "feat: add a new endpoint to get user profile information from the database"

✅
\`\`\`
feat(api): add GET /users/:id/profile

Mobile client needs profile data without the full user payload
to reduce LTE bandwidth on cold-launch screens.

Closes #128
\`\`\`

Activated via \`/caveman-commit\` or "write a commit message".

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
