# feat(skills): add ZipAI Protocol for agent behavior optimization

Source: [sickn33/antigravity-awesome-skills#517](https://github.com/sickn33/antigravity-awesome-skills/pull/517)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/zipai-optimizer/SKILL.md`

## What to add / change

# Pull Request Description

Added the `@zipai-optimizer` skill (ZipAI v11). This is a cognitive and behavioral protocol engineered for extreme AI agent token optimization. It enforces the systemic elimination of conversational filler, intelligent truncation of terminal logs and VCS operations via selective pattern matching (e.g., stacktrace isolation, hunks extraction), and permits full, detailed elaboration exclusively for architectural concepts. Designed to drastically reduce I/O payloads without compromising analytical intelligence.

## Change Classification

- [x] Skill PR
- [ ] Docs PR
- [ ] Infra PR

## Issue Link (Optional)

## Quality Bar Checklist ✅

**All applicable items must be checked before merging.**

- [x] **Standards**: I have read `docs/contributors/quality-bar.md` and `docs/contributors/security-guardrails.md`.
- [x] **Metadata**: The `SKILL.md` frontmatter is valid (checked with `npm run validate`).
- [x] **Risk Label**: I have assigned the correct `risk:` tag (`safe`).
- [x] **Triggers**: The "When to use" section is clear and specific.
- [x] **Limitations**: The skill includes a `## Limitations` (or equivalent accepted constraints) section.
- [x] **Security**: If this is an _offensive_ skill, I included the "Authorized Use Only" disclaimer.
- [x] **Safety scan**: If this PR adds or modifies `SKILL.md` command guidance, remote/network examples, or token-like strings, I ran `npm run security:docs` (or equivalent hardening check) and a

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
