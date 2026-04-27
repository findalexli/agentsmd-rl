# feat: add caveman-review skill for terse PR review comments

Source: [JuliusBrussee/caveman#45](https://github.com/JuliusBrussee/caveman/pull/45)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/caveman-review/SKILL.md`

## What to add / change

## Summary

Adds \`skills/caveman-review/SKILL.md\` — a domain-specific caveman variant for code review comments. One line per finding: location, problem, fix. Optional severity prefixes (🔴 bug / 🟡 risk / 🔵 nit / ❓ q).

## How it works

Like caveman-commit, this is domain-specific (not language-specific), so it drops the lite/full/ultra intensity model. Same family spine: Rules / Examples / Auto-Clarity / Boundaries.

Forces:
- One-line format: \`L<line>: <problem>. <fix>.\`
- Drops "I noticed that...", "you might want to consider...", "great work but..."
- Concrete fix, not "consider refactoring"
- Exact line numbers and symbol names in backticks
- Auto-clarity falls back to full prose for security findings, architectural disagreements, and onboarding contexts

## Examples

❌ "I noticed that on line 42 you're not checking if the user object is null before accessing the email property. This could potentially cause a crash..."

✅ \`L42: 🔴 bug: user can be null after .find(). Add guard before .email.\`

Activated via \`/caveman-review\` or "review this PR".

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
