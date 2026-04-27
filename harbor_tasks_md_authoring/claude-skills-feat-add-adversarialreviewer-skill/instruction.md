# feat: add adversarial-reviewer skill

Source: [alirezarezvani/claude-skills#439](https://github.com/alirezarezvani/claude-skills/pull/439)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `engineering-team/adversarial-reviewer/SKILL.md`

## What to add / change

## Summary

Adds `engineering-team/adversarial-reviewer` — a skill that breaks the self-review monoculture by forcing genuine perspective shifts through adversarial personas.

### Problem
When Claude (or any AI) reviews code it just wrote, it shares the same mental model, assumptions, and blind spots as the author. Users report this as a top frustration: "Claude reviewing Claude's code has the same blind spots" leading to "LGTM" on bugs a fresh reviewer would catch immediately.

### Solution
Three hostile reviewer personas that force different review priorities:

1. **The Saboteur** — "I'm trying to break this in production." Focuses on error paths, race conditions, resource leaks, unvalidated input.
2. **The New Hire** — "I need to modify this in 6 months with zero context." Focuses on readability, naming, implicit knowledge, maintainability.
3. **The Security Auditor** — "This code will be attacked." OWASP-informed checklist for injection, auth, data exposure, secrets.

Each persona MUST find at least one issue — no "LGTM" escapes. Findings are severity-classified (CRITICAL/WARNING/NOTE) with a promotion rule: issues caught by 2+ personas get promoted one level.

### Differentiation from existing skills
- `code-reviewer` focuses on general quality — this focuses on **perspective shift**
- `senior-security` focuses on deep security analysis — this includes security as one of three lenses
- External `adversarial-review` (alecnielsen) requires multiple models — this works with

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
