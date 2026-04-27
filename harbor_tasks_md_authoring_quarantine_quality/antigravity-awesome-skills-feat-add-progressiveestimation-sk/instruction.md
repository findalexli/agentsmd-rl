# feat: add progressive-estimation skill

Source: [sickn33/antigravity-awesome-skills#260](https://github.com/sickn33/antigravity-awesome-skills/pull/260)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/progressive-estimation/SKILL.md`

## What to add / change

## What

Adds `progressive-estimation` — a community skill for estimating AI-assisted and hybrid human+agent development work.

## Details

- Research-backed formulas with PERT statistics and confidence bands
- Adapts to human-only, hybrid, or agent-first working modes
- Supports single tasks or batch estimation (5 issues or 500)
- Outputs for Linear, JIRA, ClickUp, GitHub Issues, Monday, and GitLab
- Includes calibration feedback loop for improving accuracy over time
- Zero dependencies

**Source:** https://github.com/Enreign/progressive-estimation
**License:** MIT
**Version:** 0.3.0

## Checklist

- [x] Clear, descriptive name
- [x] Proper frontmatter (name, description, risk, source, date_added)
- [x] Examples included
- [x] Tested with AI assistant
- [x] Passes `npm run validate`
- [x] Clear commit message with conventional prefix
- [x] Checked for typos and grammar
<!-- devin-review-badge-begin -->

---

<a href="https://app.devin.ai/review/sickn33/antigravity-awesome-skills/pull/260" target="_blank">
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
