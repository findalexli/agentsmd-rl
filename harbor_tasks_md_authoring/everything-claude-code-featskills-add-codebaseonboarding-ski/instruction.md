# feat(skills): add codebase-onboarding skill

Source: [affaan-m/everything-claude-code#553](https://github.com/affaan-m/everything-claude-code/pull/553)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/codebase-onboarding/SKILL.md`

## What to add / change

## Summary
- Adds a new `codebase-onboarding` skill that analyzes unfamiliar codebases and generates structured onboarding guides + starter CLAUDE.md files
- Canonical location: `skills/codebase-onboarding/SKILL.md`

## Motivation
Every developer joining a new project faces the same ramp-up friction. This skill turns "help me understand this codebase" into a systematic 4-phase workflow that produces two actionable artifacts in under 2 minutes.

## What It Does
1. **Reconnaissance** — parallel detection of package manifests, frameworks, entry points, directory structure, tooling, and test setup
2. **Architecture mapping** — identifies tech stack, architecture pattern, key directories, and traces one request end-to-end
3. **Convention detection** — naming patterns, error handling style, async patterns, git workflow from recent history
4. **Artifact generation** — produces a scannable onboarding guide + project-specific CLAUDE.md

## Key Design Decisions
- Uses Glob/Grep for reconnaissance, not exhaustive file reads — fast even on large repos
- Enhances existing CLAUDE.md rather than replacing it
- Flags unknowns explicitly rather than guessing
- Onboarding guide targets 2-minute scannability

## Type
- [x] Skill
- [ ] Agent
- [ ] Hook
- [ ] Command

## Checklist
- [x] Follows format guidelines
- [x] Under 500 lines
- [x] Includes practical examples
- [x] Uses clear section headers
- [x] No sensitive info

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
