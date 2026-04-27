# docs: sync CLAUDE.md and AGENTS.md to v1.3.4

Source: [Nagi-ovo/gemini-voyager#467](https://github.com/Nagi-ovo/gemini-voyager/pull/467)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

## Summary
  - Sync AGENTS.md version to v1.3.4
  - Add missing "Version Bump & Release" section to AGENTS.md
  - Add sync notice to both files
  - Document `test:ui` command in testing section
  - Markdown Docs-only change, no code affected
<!-- devin-review-badge-begin -->

---

<a href="https://app.devin.ai/review/nagi-ovo/gemini-voyager/pull/467" target="_blank">
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
