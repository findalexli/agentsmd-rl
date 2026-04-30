# Update SKILL.md to final version

Source: [sickn33/antigravity-awesome-skills#305](https://github.com/sickn33/antigravity-awesome-skills/pull/305)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/analyze-project/SKILL.md`

## What to add / change

# Pull Request Description

Final updates to the merged skill:
- Added Step 0.5: Session Intent Classification for better severity/rework context
- Improved Step 6.5 severity scoring wording and added intent contextualization
- Updated anonymized sample report in examples/
- Minor cleanup and portability fixes
- npm run validate passed

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
- [x] **Risk Label**: I have assigned the correct `risk:` tag (`none`, `safe`, `critical`, `offensive`, or `unknown` for legacy/unclassified content).
- [x] **Triggers**: The "When to use" section is clear and specific.
- [x] **Security**: If this is an _offensive_ skill, I included the "Authorized Use Only" disclaimer.
- [x] **Local Test**: I have verified the skill works locally.
- [x] **Repo Checks**: I ran `npm run validate:references` if my change affected docs, workflows, or infrastructure.
- [x] **Source-Only PR**: I did not manually include generated registry artifacts (`CATALOG.md`, `skills_index.json`, `data/*.json`) in this PR.
- [x] **Credits**: I

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
