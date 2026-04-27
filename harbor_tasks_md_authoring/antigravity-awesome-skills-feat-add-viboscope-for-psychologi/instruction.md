# feat: add viboscope for psychological compatibility matching

Source: [sickn33/antigravity-awesome-skills#415](https://github.com/sickn33/antigravity-awesome-skills/pull/415)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/viboscope/SKILL.md`

## What to add / change

## Summary

Adds `viboscope`, a psychological compatibility matching skill for finding compatible cofounders, collaborators, friends, and other relationship fits through structured psychometric dimensions.

## Change Classification

- [x] Skill PR
- [ ] Docs PR
- [ ] Infra PR

## Issue Link (Optional)

Use this only when the PR should auto-close an issue:

`Closes #N` or `Fixes #N`

## Quality Bar Checklist ✅

- [x] Standards: I have read the contributor quality and security guardrails.
- [x] Metadata: The `SKILL.md` frontmatter is valid.
- [x] Risk Label: The skill is marked with an appropriate `risk:` tag.
- [x] Triggers: The "When to use" section is clear and specific.
- [x] Safety scan: The skill content is read-only and avoids risky system actions.
- [x] Automated Skill Review: I reviewed actionable workflow feedback where available.
- [x] Local Test: I validated the skill structure locally.
- [x] Repo Checks: `npm run validate` passes.
- [x] Source-Only PR: No generated registry artifacts are included.
- [x] Maintainer Edits: Allow edits from maintainers is enabled.

## Notes

- Category: collaboration
- Risk: safe
- MIT licensed upstream project reference: https://github.com/ivankoriako/viboscope

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
