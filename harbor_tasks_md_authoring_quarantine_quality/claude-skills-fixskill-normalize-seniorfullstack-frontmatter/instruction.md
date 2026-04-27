# fix(skill): normalize senior-fullstack frontmatter to inline format

Source: [alirezarezvani/claude-skills#217](https://github.com/alirezarezvani/claude-skills/pull/217)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `engineering-team/senior-fullstack/SKILL.md`

## What to add / change

## Summary

Follow-up to PR #216 — fixes consistency issues found during audit:

- **Normalized YAML frontmatter** from block scalar (`>`) to inline single-line format, matching all other 50+ skills in the repo
- **Aligned trigger phrases** in frontmatter with the body's `## Trigger Phrases` section to eliminate partial duplication
- Kept the improved description content (stack names, trigger actions) from the original PR

## Test plan

- [ ] Verify YAML frontmatter parses correctly
- [ ] Confirm description is single-line inline format
- [ ] Check trigger phrases match between frontmatter and body section

🤖 Generated with [Claude Code](https://claude.com/claude-code)
<!-- devin-review-badge-begin -->

---

<a href="https://app.devin.ai/review/alirezarezvani/claude-skills/pull/217" target="_blank">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://static.devin.ai/assets/gh-open-in-devin-review-dark.svg?v=1">
    <img src="https://static.devin.ai/assets/gh-open-in-devin-review-light.svg?v=1" alt="Open with Devin">
  </picture>
</a>
<!-- devin-review-badge-end -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
