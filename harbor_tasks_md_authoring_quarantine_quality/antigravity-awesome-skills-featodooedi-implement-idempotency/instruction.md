# feat(odoo-edi): Implement Idempotency and Secure Handling

Source: [sickn33/antigravity-awesome-skills#416](https://github.com/sickn33/antigravity-awesome-skills/pull/416)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/odoo-edi-connector/SKILL.md`

## What to add / change

# Pull Request Description

This PR refactors the `odoo-edi-connector` skill to production-grade standards. It moves the implementation from a basic script to a resilient integration by addressing critical "silent signs" of technical debt: hardcoded secrets, lack of idempotency, and runtime errors in EDI generation.

**Key Technical Improvements:**
* **Idempotency & Resource Governance**: Added a search check before `sale.order` creation to ensure the same EDI 850 doesn't create duplicate records.
* **Security Hardening**: Replaced hardcoded connection strings with `os.getenv` for all Odoo credentials (`URL`, `DB`, `API_KEY`).
* **Resilience**: Implemented a partner verification check to gracefully skip and log errors when a trading partner is not found, preventing script crashes.
* **EDI Compliance**: Fixed a `NameError` in the 997 generator by importing `datetime` and dynamically calculating the required date stamps to match X12 standards.

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
- [x] **Metadata**: The `SKILL.md` frontmatter is valid (checked with `npm run validate`).
- [x] **Risk Label**: I have assigned the correct `ris

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
