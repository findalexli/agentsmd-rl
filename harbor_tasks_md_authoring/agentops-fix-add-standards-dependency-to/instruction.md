# fix: add standards dependency to validation skills

Source: [boshu2/agentops#12](https://github.com/boshu2/agentops/pull/12)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/core-kit/skills/crank/SKILL.md`
- `plugins/general-kit/skills/validation-chain/SKILL.md`
- `plugins/general-kit/skills/vibe-docs/SKILL.md`
- `plugins/general-kit/skills/vibe/SKILL.md`
- `plugins/vibe-kit/skills/validation-chain/SKILL.md`
- `plugins/vibe-kit/skills/vibe-docs/SKILL.md`
- `plugins/vibe-kit/skills/vibe/SKILL.md`

## What to add / change

## Summary
- Added `standards` library skill as a dependency to validation-related skills
- Skills that validate code need access to language-specific standards for proper validation

## Changes
| Skill | Kit | Added Dependency |
|-------|-----|------------------|
| vibe | vibe-kit | standards |
| vibe | general-kit | standards |
| validation-chain | vibe-kit | standards |
| validation-chain | general-kit | standards |
| vibe-docs | vibe-kit | standards |
| vibe-docs | general-kit | standards |

## Rationale
The `standards` library skill provides:
- Language-specific validation rules (Python, Go, TypeScript, Shell, etc.)
- Common error tables (symptom → cause → fix)
- Anti-patterns to detect
- AI agent guidelines (ALWAYS/NEVER rules)

Without this dependency declared, the skills cannot load the standards references during validation.

## Test plan
- [ ] Verify skills load without errors
- [ ] Run `/vibe recent` and confirm it can access standards references

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
