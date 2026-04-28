# feat: add latex-paper-conversion skill

Source: [sickn33/antigravity-awesome-skills#296](https://github.com/sickn33/antigravity-awesome-skills/pull/296)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/latex-paper-conversion/SKILL.md`

## What to add / change

# Pull Request Description

Adds a new skill: `latex-paper-conversion`. This skill assists AI models in properly formatting and structuring text into LaTeX code, which is especially useful for streamlining academic research papers and journal submissions.

## Change Classification

- [x] Skill PR
- [ ] Docs PR
- [ ] Infra PR

## Issue Link (Optional)

*(Left blank as there is no linked issue)*

## Quality Bar Checklist ✅

**All items must be checked before merging.**

- [x] **Standards**: I have read `docs/contributors/quality-bar.md` and `docs/contributors/security-guardrails.md`.
- [x] **Metadata**: The `SKILL.md` frontmatter is valid (checked with `npm run validate`).
- [x] **Risk Label**: I have assigned the correct `risk:` tag (`none`, `safe`, `critical`, `offensive`, or `unknown` for legacy/unclassified content).
- [x] **Triggers**: The "When to use" section is clear and specific.
- [x] **Security**: If this is an _offensive_ skill, I included the "Authorized Use Only" disclaimer. *(N/A for this safe skill)*
- [x] **Local Test**: I have verified the skill works locally.
- [x] **Repo Checks**: I ran `npm run validate:references` if my change affected docs, workflows, or infrastructure. *(N/A for skill-only PR)*
- [x] **Source-Only PR**: I did not manually include generated registry artifacts (`CATALOG.md`, `skills_index.json`, `data/*.json`) in this PR.
- [x] **Credits**: I have added the source credit in `README.md` (if applicable).
- [x] **Ma

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
