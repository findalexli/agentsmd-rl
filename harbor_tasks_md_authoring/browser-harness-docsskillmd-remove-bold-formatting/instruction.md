# docs(SKILL.md): remove bold formatting

Source: [browser-use/browser-harness#177](https://github.com/browser-use/browser-harness/pull/177)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `SKILL.md`

## What to add / change

Remove all `**bold**` markers from SKILL.md for a cleaner, more consistent plain-text style.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

<!-- This is an auto-generated description by cubic. -->
---
## Summary by cubic
Removed all bold emphasis from `SKILL.md` to use a clean, consistent plain‑text style and reduce visual noise. Minimal content changes; one inline code example was adjusted to avoid Markdown bold conflicts.

- **Refactors**
  - Stripped `**` markers from headings, lists, and inline phrases.
  - Updated example to `cdp("Domain.method", params)` to avoid `**` being parsed as bold in code spans.

<sup>Written for commit 3dfb08a73d274299de3b248463ef9e16c5b130c9. Summary will update on new commits.</sup>

<!-- End of auto-generated description by cubic. -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
