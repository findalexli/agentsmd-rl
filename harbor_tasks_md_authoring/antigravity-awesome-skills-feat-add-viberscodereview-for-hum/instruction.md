# feat: add vibers-code-review for human review of AI-generated code

Source: [sickn33/antigravity-awesome-skills#325](https://github.com/sickn33/antigravity-awesome-skills/pull/325)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/vibers-code-review/SKILL.md`

## What to add / change

## Summary

- Adds **vibers-code-review** skill — human code review for AI-generated projects
- Reviews spec compliance, security (OWASP top 10), AI hallucinations, logic bugs
- Submits PRs with fixes directly to the repo
- GitHub Action: [marsiandeployer/vibers-action](https://github.com/marsiandeployer/vibers-action)

## Change Classification

- [x] Skill PR
- [ ] Docs PR
- [ ] Infra PR

## Issue Link (Optional)

N/A

## Quality Bar Checklist ✅

- [x] Standards: I have read the contributor quality and security guides.
- [x] Metadata: The SKILL.md frontmatter is valid.
- [x] Risk Label: Assigned appropriately for this skill.
- [x] Triggers: The When to use section is clear and specific.
- [x] Security: Execution guidance is framed as review workflow, not unsafe repository mutation.
- [x] Safety scan: Command and network guidance reviewed.
- [x] Automated Skill Review: The skill-review result was reviewed.
- [x] Local Test: Validation was run locally before submission.
- [x] Repo Checks: No workflow or infra changes beyond the skill file.
- [x] Source-Only PR: No derived registry artifacts included.
- [x] Credits: Not applicable.
- [x] Maintainer Edits: Allow edits from maintainers is enabled.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
