# refactor: consolidate .claude/rules into CLAUDE.md and skill

Source: [max-sixty/worktrunk#791](https://github.com/max-sixty/worktrunk/pull/791)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/rules/accessor-conventions.md`
- `.claude/rules/caching-strategy.md`
- `.claude/rules/output-system-architecture.md`
- `.claude/skills/writing-user-outputs/SKILL.md`
- `CLAUDE.md`

## What to add / change

## Summary

- Create `writing-user-outputs` skill from output formatting + architecture docs (887 lines)
- Add accessor conventions and caching strategy to CLAUDE.md (always loaded)
- Delete `.claude/rules/` directory (4 files)

The output formatting docs are detailed reference material better suited to on-demand skill loading. The accessor and caching docs are small enough (~130 lines combined) to inline into CLAUDE.md where they're always available.

**Before:**
```
CLAUDE.md (317 lines)
.claude/rules/
├── accessor-conventions.md (64 lines)
├── caching-strategy.md (69 lines)
├── cli-output-formatting.md (776 lines)
└── output-system-architecture.md (115 lines)
```

**After:**
```
CLAUDE.md (411 lines)
.claude/skills/
├── release/SKILL.md
└── writing-user-outputs/SKILL.md (887 lines)
```

## Test plan

- [x] Pre-commit lints pass
- [ ] CI passes

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
