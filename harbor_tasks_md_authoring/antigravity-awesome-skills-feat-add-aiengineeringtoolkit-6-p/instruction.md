# feat: add ai-engineering-toolkit — 6 production-ready AI engineering skills

Source: [sickn33/antigravity-awesome-skills#314](https://github.com/sickn33/antigravity-awesome-skills/pull/314)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/ai-engineering-toolkit/SKILL.md`

## What to add / change

# Pull Request Description

Adds **ai-engineering-toolkit** as a new in-repo skill at `skills/ai-engineering-toolkit/SKILL.md`.

The toolkit bundles six AI engineering workflows: prompt evaluation, context budget planning, RAG architecture, agent safety review, eval harness design, and product-sense coaching.

## Change Classification

- [x] Skill PR
- [ ] Docs PR
- [ ] Infra PR

## Issue Link (Optional)

Use this only when the PR should auto-close an issue:

`Closes #N` or `Fixes #N`

## Quality Bar Checklist ✅

**All items must be checked before merging.**

- [x] **Standards**: I have read `docs/contributors/quality-bar.md` and `docs/contributors/security-guardrails.md`.
- [x] **Metadata**: The added `SKILL.md` contains repository-compatible frontmatter.
- [x] **Risk Label**: The skill is classified for repository review and may be adjusted during maintainer validation if needed.
- [x] **Triggers**: The skill content includes a clear “When to Use This Skill” section.
- [x] **Security**: Any security-oriented guidance will be validated against the repository’s offensive-skill guardrails before merge.
- [x] **Safety scan**: Reviewed for documentation safety and repository policy fit.
- [x] **Local Test**: Verified the added skill content locally.
- [x] **Repo Checks**: `npm run validate` is the primary repository gate for this skill addition.
- [x] **Source-Only PR**: No generated registry artifacts (`CATALOG.md`, `skills_index.json`, `data/*.json`) are included.
- [x] **Cred

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
