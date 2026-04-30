# feat: Update .claude skills to PostgreSQL 18

Source: [yonatangross/orchestkit#5](https://github.com/yonatangross/orchestkit/pull/5)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/agents/database-engineer.md`
- `.claude/skills/api-design-framework/examples/skillforge-api-design.md`
- `.claude/skills/langgraph-human-in-loop/SKILL.md`
- `.claude/skills/langgraph-supervisor/examples/skillforge-analysis-workflow.md`
- `.claude/skills/observability-monitoring/SKILL.md`
- `.claude/skills/observability-monitoring/checklists/monitoring-implementation-checklist.md`
- `.claude/skills/pgvector-search/references/metadata-filtering.md`
- `.claude/skills/unit-testing/examples/skillforge-test-strategy.md`

## What to add / change

## Summary
- Syncs plugin with SkillForge's PostgreSQL 18 upgrade
- Updates database-engineer agent: pg17 → pg18
- Updates unit-testing CI example: pgvector/pgvector:pg18
- Syncs api-design-framework with UUID v7 server_default patterns
- Syncs langgraph-supervisor with pg18 UUID generation
- Updates observability-monitoring patterns
- Syncs pgvector-search metadata filtering
- Syncs langgraph-human-in-loop workflow improvements

## Files Changed
| File | Change |
|------|--------|
| `database-engineer.md` | PostgreSQL 17 → 18 |
| `skillforge-test-strategy.md` | pgvector:pg17 → pg18 |
| `skillforge-api-design.md` | UUID v7 server_default |
| `skillforge-analysis-workflow.md` | pg18 UUID generation |
| `observability-monitoring/*` | Pattern updates |
| `pgvector-search/*` | Metadata filtering |
| `langgraph-human-in-loop/*` | Workflow improvements |

## Test plan
- [ ] Verify skill examples reference pg18
- [ ] Confirm database-engineer agent targets pg18

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
