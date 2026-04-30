# feat: add avoid-ai-writing skill

Source: [sickn33/antigravity-awesome-skills#212](https://github.com/sickn33/antigravity-awesome-skills/pull/212)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/avoid-ai-writing/SKILL.md`

## What to add / change

# Pull Request Description

Adds avoid-ai-writing, a skill that audits and rewrites content to remove 21 categories of AI writing patterns. Includes a 43-entry word/phrase replacement table with specific alternatives and a structured four-section output with second-pass audit.

Source: https://github.com/conorbronsdon/avoid-ai-writing

## Quality Bar Checklist

- [x] **Standards**: I have read `docs/QUALITY_BAR.md` and `docs/SECURITY_GUARDRAILS.md`.
- [x] **Metadata**: The `SKILL.md` frontmatter is valid.
- [x] **Risk Label**: I have assigned the correct `risk:` tag (`none`).
- [x] **Triggers**: The "When to use" section is clear and specific.
- [x] **Security**: Not an offensive skill — no disclaimer needed.
- [x] **Local Test**: I have verified the skill works locally.
- [x] **Credits**: Source credit included in frontmatter.

## Type of Change

- [x] New Skill (Feature)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
