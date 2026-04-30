# Add hierarchical-agent-memory skill

Source: [sickn33/antigravity-awesome-skills#160](https://github.com/sickn33/antigravity-awesome-skills/pull/160)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/hierarchical-agent-memory/SKILL.md`

## What to add / change

## Summary

- Adds `hierarchical-agent-memory` (HAM) — a scoped CLAUDE.md memory system that reduces context token spend by giving agents directory-level cheat sheets instead of re-reading entire projects
- Includes 7 commands: `go ham`, `ham savings`, `ham dashboard`, `ham audit`, `ham insights`, `ham route`, `ham carbon`
- Features a web dashboard for visualizing token savings, session history, context health, and routing compliance
- Source repo: https://github.com/kromahlusenii-ops/ham (18 stars)

## Checklist

- [x] Created `skills/hierarchical-agent-memory/SKILL.md` with required frontmatter (`name`, `description`, `risk`, `source`, `date_added`)
- [x] `npm run validate` passes (951 skills, 0 errors)
- [x] `npm run validate:strict` passes
- [x] Risk level: `safe` (reads files, generates markdown files)
- [x] Includes triggers, examples, best practices, and limitations sections

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
