# docs(wordpress-seo-skill): update skill documentation with enhanced structure

Source: [sickn33/antigravity-awesome-skills#553](https://github.com/sickn33/antigravity-awesome-skills/pull/553)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/social-post-writer-seo/SKILL.md`
- `skills/wordpress-centric-high-seo-optimized-blogwriting-skill/SKILL.md`

## What to add / change

# Pull Request Description

Please include a summary of the change and which skill is added or fixed.

## Change Classification

- [x] Skill PR
- [x] Docs PR
- [ ] Infra PR

## Issue Link (Optional)

Use this only when the PR should auto-close an issue:

`Closes #N` or `Fixes #N`

## Quality Bar Checklist ✅

**All applicable items must be checked before merging.**

- [x] **Standards**: I have read `docs/contributors/quality-bar.md` and `docs/contributors/security-guardrails.md`.
- [ ] **Metadata**: The `SKILL.md` frontmatter is valid (checked with `npm run validate`).
- [ ] **Risk Label**: I have assigned the correct `risk:` tag (`none`, `safe`, `critical`, `offensive`, or `unknown` for legacy/unclassified content).
- [ ] **Triggers**: The "When to use" section is clear and specific.
- [ ] **Limitations**: The skill includes a `## Limitations` (or equivalent accepted constraints) section.
- [ ] **Security**: If this is an _offensive_ skill, I included the "Authorized Use Only" disclaimer.
- [ ] **Safety scan**: If this PR adds or modifies `SKILL.md` command guidance, remote/network examples, or token-like strings, I ran `npm run security:docs` (or equivalent hardening check) and addressed any findings.
- [ ] **Automated Skill Review**: If this PR changes `SKILL.md`, I checked the `skill-review` GitHub Actions result and addressed any actionable feedback.
- [ ] **Manual Logic Review**: If this PR changes `SKILL.md` or risky guidance, I manually revi

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
