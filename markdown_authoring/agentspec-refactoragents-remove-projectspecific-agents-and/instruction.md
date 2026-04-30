# refactor(agents): remove project-specific agents and reorganize structure

Source: [luanmorenommaciel/agentspec#2](https://github.com/luanmorenommaciel/agentspec/pull/2)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/agents/code-quality/dual-reviewer.md`
- `.claude/agents/dev/dev-loop-executor.md`
- `.claude/agents/dev/prompt-crafter.md`
- `.claude/agents/developer/python-developer.md`
- `.claude/agents/domain/dataops-builder.md`
- `.claude/agents/domain/extraction-specialist.md`
- `.claude/agents/domain/function-developer.md`
- `.claude/agents/domain/infra-deployer.md`
- `.claude/agents/domain/pipeline-architect.md`

## What to add / change

## Summary

- **Sanitize agent library** for public AgentSpec framework distribution
- **Remove project-specific agents** that referenced internal tooling
- **Reorganize structure** with new `developer/` directory

### Key Changes
- Remove 8 project-specific agent definitions
- Move `python-developer.md` to `developer/` directory
- Clean up empty directories

## What's Changed

### Removed Agents

| Directory | Agent | Reason |
|-----------|-------|--------|
| `domain/` | dataops-builder | Project-specific |
| `domain/` | extraction-specialist | Project-specific |
| `domain/` | function-developer | Project-specific |
| `domain/` | infra-deployer | Project-specific |
| `domain/` | pipeline-architect | Project-specific |
| `dev/` | dev-loop-executor | Project-specific workflow |
| `dev/` | prompt-crafter | Project-specific workflow |
| `code-quality/` | dual-reviewer | References external tools |

### Reorganized

| From | To | Reason |
|------|-----|--------|
| `code-quality/python-developer.md` | `developer/python-developer.md` | Better categorization |

## Files Changed

| Category | Files | Description |
|----------|-------|-------------|
| Deleted | 8 | Project-specific agent definitions |
| Renamed | 1 | Reorganized to developer/ |

## Test Plan

- [ ] Verify remaining agents load correctly in Claude Code
- [ ] Confirm no broken references in commands or workflows
- [ ] Test `/build` and `/review` commands still work

## Breaking Changes

None - removed agents were projec

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
