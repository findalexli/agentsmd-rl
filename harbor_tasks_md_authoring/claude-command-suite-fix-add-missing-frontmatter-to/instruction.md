# fix: add missing frontmatter to agent files

Source: [qdhenry/Claude-Command-Suite#32](https://github.com/qdhenry/Claude-Command-Suite/pull/32)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/agents/TASK-STATUS-PROTOCOL.md`
- `.claude/agents/dependency-analyzer.md`
- `.claude/agents/task-commit-manager.md`
- `.claude/agents/task-decomposer.md`
- `.claude/agents/task-orchestrator.md`

## What to add / change

## Summary
- Fixed 5 agent files that were causing parse errors due to missing frontmatter
- Added required YAML frontmatter fields: `name`, `description`, and `tools`
- Each file now includes complete agent documentation

## Fixed Files
1. **task-commit-manager.md** - Manages git commits and task completion workflows
2. **TASK-STATUS-PROTOCOL.md** - Defines task status transitions and lifecycle management
3. **task-orchestrator.md** - Orchestrates complex multi-step tasks with dependencies
4. **task-decomposer.md** - Breaks down projects into atomic, actionable tasks
5. **dependency-analyzer.md** - Analyzes and manages project dependencies

## Test Plan
- [x] All agent files now have valid YAML frontmatter
- [x] Each file includes the required `name` field
- [x] Each file includes a descriptive `description` field
- [x] Each file specifies the `tools` they use
- [ ] Run `claude doctor` to verify no parse errors remain

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
