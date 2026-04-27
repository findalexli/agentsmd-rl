# fix(front-matter): code-reviewer, architect-review and etc.

Source: [sickn33/antigravity-awesome-skills#111](https://github.com/sickn33/antigravity-awesome-skills/pull/111)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/architect-review/SKILL.md`
- `skills/c-pro/SKILL.md`
- `skills/code-reviewer/SKILL.md`
- `skills/design-orchestration/SKILL.md`
- `skills/haskell-pro/SKILL.md`
- `skills/multi-agent-brainstorming/SKILL.md`
- `skills/performance-engineer/SKILL.md`
- `skills/search-specialist/SKILL.md`

## What to add / change

# Pull Request Description

Wrong front matter in architect-review. Tested by yq-go, `yq --front-matter=format SKILL.md`.

## Quality Bar Checklist ✅

**All items must be checked before merging.**

- [ ] **Standards**: I have read `docs/QUALITY_BAR.md` and `docs/SECURITY_GUARDRAILS.md`.
- [ ] **Metadata**: The `SKILL.md` frontmatter is valid (checked with `scripts/validate_skills.py`).
- [ ] **Risk Label**: I have assigned the correct `risk:` tag (`none`, `safe`, `critical`, `offensive`).
- [ ] **Triggers**: The "When to use" section is clear and specific.
- [ ] **Security**: If this is an _offensive_ skill, I included the "Authorized Use Only" disclaimer.
- [x] **Local Test**: I have verified the skill works locally.
- [ ] **Credits**: I have added the source credit in `README.md` (if applicable).

## Type of Change

- [ ] New Skill (Feature)
- [ ] Documentation Update
- [ ] Infrastructure

## Screenshots (if applicable)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
