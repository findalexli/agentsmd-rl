# feat: Add Claude Code agents, skills, and rules

Source: [fullstackhero/dotnet-starter-kit#1166](https://github.com/fullstackhero/dotnet-starter-kit/pull/1166)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/agents/architecture-guard.md`
- `.claude/agents/code-reviewer.md`
- `.claude/agents/feature-scaffolder.md`
- `.claude/agents/migration-helper.md`
- `.claude/agents/module-creator.md`
- `.claude/rules/api-conventions.md`
- `.claude/rules/buildingblocks-protection.md`
- `.claude/rules/testing-rules.md`
- `.claude/skills/add-entity/SKILL.md`
- `.claude/skills/add-feature/SKILL.md`
- `.claude/skills/add-module/SKILL.md`
- `.claude/skills/mediator-reference/SKILL.md`
- `.claude/skills/query-patterns/SKILL.md`
- `.claude/skills/testing-guide/SKILL.md`
- `CLAUDE.md`

## What to add / change

## Summary

Restructured `.claude/` folder to follow [Claude Code official documentation](https://code.claude.com/docs/en/skills).

## Changes

### Skills (`.claude/skills/<name>/SKILL.md`)
| Skill | Purpose |
|-------|---------|
| `add-feature` | Create API endpoints with vertical slice pattern |
| `add-module` | Scaffold new bounded contexts |
| `add-entity` | Create domain entities with multi-tenancy |
| `query-patterns` | Pagination, filtering, specifications |
| `testing-guide` | Unit, integration, architecture tests |
| `mediator-reference` | Mediator vs MediatR (background knowledge) |

### Subagents (`.claude/agents/<name>.md`)
| Agent | Purpose | Model |
|-------|---------|-------|
| `code-reviewer` | Review PRs against FSH patterns | sonnet (read-only) |
| `feature-scaffolder` | Generate complete feature files | inherit |
| `module-creator` | Scaffold new modules | inherit |
| `architecture-guard` | Verify architecture | haiku (plan mode) |
| `migration-helper` | EF Core migrations | inherit |

### Rules (`.claude/rules/<name>.md`) - Path-scoped
| Rule | Triggers On |
|------|-------------|
| `buildingblocks-protection` | `src/BuildingBlocks/**/*` |
| `api-conventions` | `src/Modules/**/Features/**/*` |
| `testing-rules` | `src/Tests/**/*` |

## Removed
- Old flat files: `skills.md`, `agents.md`, `rules.md`

## Updated
- `CLAUDE.md` with new structure reference

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
