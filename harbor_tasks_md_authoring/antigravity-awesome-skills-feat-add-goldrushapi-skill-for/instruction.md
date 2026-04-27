# feat: add goldrush-api skill for blockchain data across 100+ chains

Source: [sickn33/antigravity-awesome-skills#334](https://github.com/sickn33/antigravity-awesome-skills/pull/334)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/goldrush-api/SKILL.md`

## What to add / change

# Pull Request Description

Adds a `goldrush-api` skill for querying blockchain data via the GoldRush API by Covalent.

## Change Classification

- [x] Skill PR
- [ ] Docs PR
- [ ] Infra PR

## Issue Link (Optional)

No linked issue.

## Quality Bar Checklist ✅

**All items must be checked before merging.**

- [x] **Standards**: Maintainer-reviewed against the repository Quality Bar and security guardrails for merge readiness.
- [x] **Metadata**: The `SKILL.md` frontmatter is valid and the automated skill review is green.
- [x] **Risk Label**: The skill is labeled `risk: safe`.
- [x] **Triggers**: The skill purpose and usage are specific to GoldRush API workflows.
- [x] **Security**: This is non-offensive, read-only API guidance.
- [x] **Safety scan**: The rerun CI path includes the docs security checks required for `SKILL.md` changes.
- [x] **Automated Skill Review**: The `skill-review` workflow is green.
- [x] **Local Test**: Merge decision is based on maintainer review plus CI validation for this source-only PR.
- [x] **Repo Checks**: This PR is being revalidated through the repository CI workflow.
- [x] **Source-Only PR**: No generated registry artifacts are included in this PR.
- [x] **Credits**: Source links are included in the PR body; no additional README credit was required for this maintainer merge decision.
- [x] **Maintainer Edits**: Maintainer review/edit path is being used to normalize the PR for policy compliance.

## Screenshots (if applicable)

N/A

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
