# Add windows-shell-reliability skill

Source: [sickn33/antigravity-awesome-skills#386](https://github.com/sickn33/antigravity-awesome-skills/pull/386)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/windows-shell-reliability/SKILL.md`

## What to add / change

# Pull Request Description

This PR adds the `windows-shell-reliability` skill to the repository. This skill provides best practices for running commands on Windows via PowerShell and CMD, focusing on encoding, path handling, and common binary pitfalls.

## Change Classification

- [x] Skill PR
- [ ] Docs PR
- [ ] Infra PR

## Issue Link (Optional)

N/A

## Quality Bar Checklist ✅

**All items must be checked before merging.**

- [x] **Standards**: I have read `docs/contributors/quality-bar.md` and `docs/contributors/security-guardrails.md`.
- [x] **Metadata**: The `SKILL.md` frontmatter is valid (checked with `npm run validate`).
- [x] **Risk Label**: I have assigned the correct `risk:` tag (`safe`).
- [x] **Triggers**: The "When to use" section is clear and specific.
- [ ] **Security**: If this is an _offensive_ skill, I included the "Authorized Use Only" disclaimer. (N/A)
- [x] **Safety scan**: If this PR adds or modifies `SKILL.md` command guidance, remote/network examples, or token-like strings, I ran `npm run security:docs` and addressed any findings.
- [ ] **Automated Skill Review**: Checked local validation; GA results to be reviewed upon submission.
- [x] **Local Test**: I have verified the skill works locally.
- [x] **Repo Checks**: Ran `npm run validate` which covers skill metadata and structure.
- [x] **Source-Only PR**: I did not manually include generated registry artifacts.
- [ ] **Credits**: N/A
- [x] **Maintainer Edits**: I enable

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
