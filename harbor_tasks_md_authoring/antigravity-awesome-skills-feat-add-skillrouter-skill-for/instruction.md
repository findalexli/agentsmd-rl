# feat: add skill-router skill for intelligent skill recommendation

Source: [sickn33/antigravity-awesome-skills#189](https://github.com/sickn33/antigravity-awesome-skills/pull/189)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/skill-router/SKILL.md`

## What to add / change

## Pull Request Description

`@skill-router` is a meta-skill that acts as an intelligent entry point to
the skill library. It interviews users who are unsure what they want to do
with a 4-question funnel, then recommends the best skill(s) with an exact
invoke prompt to copy-paste immediately.

This fills a gap in the library. With 900+ skills, new users often don't
know where to start. This skill solves that by acting as a guided router
before any other skill is invoked.

## Quality Bar Checklist ✅

- [x] **Standards**: I have read `docs/QUALITY_BAR.md` and `docs/SECURITY_GUARDRAILS.md`.
- [x] **Metadata**: The `SKILL.md` frontmatter is valid (checked with `scripts/validate_skills.py`).
- [x] **Risk Label**: `risk: safe` — reads context, asks questions, no file writes or commands.
- [x] **Triggers**: `## When to Use` section is clear and specific.
- [ ] **Security**: N/A — not an offensive skill.
- [x] **Local Test**: Verified working locally in Antigravity IDE.
- [x] **Credits**: Original skill — `source: self`.

## Type of Change

- [x] New Skill (Feature)

## Screenshots (not applicable)

### Example interaction

**User:** `@skill-router I want to build something but I'm not sure where to start`

**Agent asks 4 questions:**
1. Broad area → Building
2. How specific → Rough idea
3. Tech stack → Next.js
4. Working style → Collaborative

**Agent responds:**
> ✅ Primary: `@brainstorming` — shapes rough ideas into a clear spec
> 🔁 Also: `@p

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
