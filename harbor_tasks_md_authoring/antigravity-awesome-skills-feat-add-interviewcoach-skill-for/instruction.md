# feat: add interview-coach skill for full job search lifecycle coaching

Source: [sickn33/antigravity-awesome-skills#272](https://github.com/sickn33/antigravity-awesome-skills/pull/272)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/interview-coach/SKILL.md`

## What to add / change

## Summary
- add `interview-coach`, a persistent coaching system for the full job search lifecycle
- covers JD decoding, resume review, storybank building, mock interviews, transcript analysis, and negotiation support

## Quality Bar Checklist ✅
- [x] **Standards**: I have read `docs/contributors/quality-bar.md` and `docs/contributors/security-guardrails.md`.
- [x] **Metadata**: The `SKILL.md` frontmatter is valid (checked with `npm run validate`).
- [x] **Risk Label**: I assigned the correct `risk:` tag.
- [x] **Triggers**: The "When to use" section is clear and specific.
- [x] **Security**: This is not an offensive skill.
- [x] **Local Test**: I verified the skill locally.
- [x] **Repo Checks**: I ran the validation chain and catalog sync required for skills changes.
- [x] **Credits**: Source attribution is included in the skill.

## Type of Change
- [x] New Skill (Feature)
- [ ] Documentation Update
- [ ] Infrastructure

## Source
- https://github.com/dbhat93/job-search-os

## Verification
- `npm run validate`
- `npm run chain`
- `npm run catalog`

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
