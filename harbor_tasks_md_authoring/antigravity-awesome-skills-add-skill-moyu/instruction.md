# Add skill: moyu

Source: [sickn33/antigravity-awesome-skills#384](https://github.com/sickn33/antigravity-awesome-skills/pull/384)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/moyu/SKILL.md`

## What to add / change

# Pull Request Description

This PR adds the `moyu` skill to help AI coding agents avoid over-engineering and keep changes tightly scoped to the user's request.

## Change Classification

- [x] Skill PR
- [ ] Docs PR
- [ ] Infra PR

## Issue Link (Optional)

N/A

## Quality Bar Checklist ✅

**All items must be checked before merging.**

- [x] **Standards**: Reviewed against `docs/contributors/quality-bar.md` and `docs/contributors/security-guardrails.md` during maintainer cleanup.
- [x] **Metadata**: Frontmatter now validates and matches the skill directory.
- [ ] **Risk Label**: Legacy/community metadata still needs explicit `risk:` frontmatter if the contributor wants to eliminate warnings.
- [x] **Triggers**: The skill intent and activation behavior are clear in the body content.
- [ ] **Security**: N/A (not an offensive skill).
- [x] **Safety scan**: Maintainer ran `npm run security:docs` while stabilizing the PR.
- [ ] **Automated Skill Review**: Waiting on refreshed GitHub Actions runs after maintainer fixes.
- [x] **Local Test**: Maintainer ran `npm run validate` after correcting the frontmatter mismatch and description length.
- [x] **Repo Checks**: Validation passes after the maintainer fix.
- [x] **Source-Only PR**: No generated registry artifacts are included.
- [x] **Credits**: Source noted from https://github.com/uucz/moyu.
- [x] **Maintainer Edits**: Enabled.

## Screenshots (if applicable)

N/A

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
