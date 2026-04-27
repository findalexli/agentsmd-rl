# Highlight durable execution in relevant architectural skills

Source: [sickn33/antigravity-awesome-skills#184](https://github.com/sickn33/antigravity-awesome-skills/pull/184)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/ai-agents-architect/SKILL.md`
- `skills/architecture-patterns/SKILL.md`
- `skills/event-sourcing-architect/SKILL.md`
- `skills/saga-orchestration/SKILL.md`
- `skills/workflow-automation/SKILL.md`

## What to add / change

# Pull Request Description

Highlight durable execution in relevant architectural skills

## Quality Bar Checklist ✅

**All items must be checked before merging.**

- [x] **Standards**: I have read `docs/QUALITY_BAR.md` and `docs/SECURITY_GUARDRAILS.md`.
- [x] **Metadata**: The `SKILL.md` frontmatter is valid (checked with `scripts/validate_skills.py`).
- [x] **Risk Label**: I have assigned the correct `risk:` tag (`none`, `safe`, `critical`, `offensive`).
- [x] **Triggers**: The "When to use" section is clear and specific.
- [x] **Security**: If this is an _offensive_ skill, I included the "Authorized Use Only" disclaimer.
- [x] **Local Test**: I have verified the skill works locally.
- [x] **Credits**: I have added the source credit in `README.md` (if applicable).

## Type of Change

- [ ] New Skill (Feature)
- [x] Documentation Update
- [ ] Infrastructure

## Screenshots (if applicable)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
