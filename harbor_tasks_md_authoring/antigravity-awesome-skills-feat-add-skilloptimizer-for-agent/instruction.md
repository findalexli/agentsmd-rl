# feat: add skill-optimizer for Agent Skills diagnostics

Source: [sickn33/antigravity-awesome-skills#490](https://github.com/sickn33/antigravity-awesome-skills/pull/490)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/skill-optimizer/SKILL.md`

## What to add / change

## Summary

Adds **[skill-optimizer](https://github.com/hqhq1025/skill-optimizer)** (MIT, 46+ stars) to the skills catalog.

- **What it does**: Diagnoses and optimizes Agent Skills (SKILL.md) using real session data + research-backed static analysis across 8 dimensions (trigger rate, user reaction, workflow completion, static quality, undertrigger detection, cross-skill conflicts, environment consistency, token economics).
- **Compatibility**: Works with Claude Code, Codex, and any Agent Skills-compatible agent.
- **Install**: `npx skills add hqhq1025/skill-optimizer`
- **Risk**: `safe` (read-only analysis, never modifies skill files)

## Change Classification

- [ ] Skill PR
- [ ] Docs PR
- [ ] Infra PR

## Issue Link (Optional)

Use this only when the PR should auto-close an issue:

`Closes #N` or `Fixes #N`

## Quality Bar Checklist ✅

**All applicable items must be checked before merging.**

- [ ] **Standards**: I have read `docs/contributors/quality-bar.md` and `docs/contributors/security-guardrails.md`.
- [ ] **Metadata**: The `SKILL.md` frontmatter is valid (checked with `npm run validate`).
- [ ] **Risk Label**: I have assigned the correct `risk:` tag (`none`, `safe`, `critical`, `offensive`, or `unknown` for legacy/unclassified content).
- [ ] **Triggers**: The "When to use" section is clear and specific.
- [ ] **Security**: If this is an _offensive_ skill, I included the "Authorized Use Only" disclaimer.
- [ ] **Safety scan**: If this PR adds or modifies `SKILL.md`

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
