# feat: add openclaw-github-repo-commander for GitHub repo audit and cleanup

Source: [sickn33/antigravity-awesome-skills#340](https://github.com/sickn33/antigravity-awesome-skills/pull/340)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/openclaw-github-repo-commander/SKILL.md`

## What to add / change

# Pull Request Description

Adds the `openclaw-github-repo-commander` skill for comprehensive GitHub repository audit and cleanup workflows.

## Change Classification

- [x] Skill PR
- [ ] Docs PR
- [ ] Infra PR

## Issue Link (Optional)

No linked issue.

## Quality Bar Checklist ✅

**All items must be checked before merging.**

- [x] **Standards**: Maintainer-reviewed against the repository Quality Bar and security guardrails for merge readiness.
- [x] **Metadata**: The `SKILL.md` frontmatter is present and the automated skill review is green.
- [x] **Risk Label**: The skill is labeled `risk: safe`.
- [x] **Triggers**: The trigger phrases and use case are specific to repository audit and cleanup tasks.
- [x] **Security**: This is non-offensive maintenance guidance.
- [x] **Safety scan**: The rerun CI path includes the docs security checks required for `SKILL.md` changes.
- [x] **Automated Skill Review**: The `skill-review` workflow is green.
- [x] **Local Test**: Merge decision is based on maintainer review plus CI validation for this source-only PR.
- [x] **Repo Checks**: This PR is being revalidated through the repository CI workflow.
- [x] **Source-Only PR**: No generated registry artifacts are included in this PR.
- [x] **Credits**: External repository attribution is present in the PR body.
- [x] **Maintainer Edits**: Maintainer review/edit path is being used to normalize the PR for policy compliance.

## Screenshots (if applicable)

N/A

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
