# Add AWT — AI-powered E2E testing skill (beta, feedback welcome)

Source: [sickn33/antigravity-awesome-skills#320](https://github.com/sickn33/antigravity-awesome-skills/pull/320)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/awt-e2e-testing/SKILL.md`

## What to add / change

# Pull Request Description

Adds **AWT (AI Watch Tester)** as a new in-repo skill at `skills/awt-e2e-testing/SKILL.md`.

The skill covers AI-assisted end-to-end web testing with declarative YAML scenarios, Playwright execution, visual matching, platform auto-detection, and structured failure diagnosis.

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
- [x] **Metadata**: The PR adds a single `SKILL.md` file with valid frontmatter for repository validation.
- [x] **Risk Label**: This is a testing skill and is treated as safe/read-focused guidance.
- [x] **Triggers**: The skill content explains when to use AWT for browser-based E2E testing.
- [x] **Security**: Not an offensive skill.
- [x] **Safety scan**: The install and usage guidance was reviewed for doc-safety concerns.
- [x] **Local Test**: Verified the added skill content and metadata locally.
- [x] **Repo Checks**: `npm run validate` is the primary repository gate for this skill addition.
- [x] **Source-Only PR**: No generated registry artifacts (`CATALOG.md`, `skills_index.json`, `data/*.json`) are included.
- [x] **Credits**: Source repositories are linked in the skill content.
- [x] **Maintainer Edits**

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
