# feat(skills): add orch-runtime — persistent AI agent team dispatch from Claude Code

Source: [affaan-m/everything-claude-code#559](https://github.com/affaan-m/everything-claude-code/pull/559)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/orch-runtime/SKILL.md`

## What to add / change

## Summary

Adds `skills/orch-runtime/SKILL.md` — an integration skill for [ORCH](https://github.com/oxgeneral/ORCH) (`@oxgeneral/orch`), a TypeScript CLI runtime for coordinating persistent AI agent teams.

**Why this fits ECC:**
- ECC excels at in-session multi-agent orchestration (`/orchestrate`, `/multi-plan`, `/multi-execute`)
- ORCH solves the complementary problem: **persistent, stateful agent workflows** that survive multiple Claude sessions
- Together: ECC handles in-process planning → ORCH handles long-running async execution with state machine accountability

**What the skill teaches:**
- Install and bootstrap ORCH alongside Claude Code
- Dispatch tasks to a persistent agent team (`orch task add`)
- Pass context between ECC sessions and ORCH agents (`orch context set/get`)
- Hybrid workflow: `/orchestrate` for planning → ORCH for execution
- Inter-agent messaging, goal hierarchies, auto-retry patterns
- Programmatic API (`@oxgeneral/orch` as npm library)

## Type

- [x] Skill

## Testing

Tested against ORCH v0.3+ with Claude adapter:
```bash
npm install -g @oxgeneral/orch
orch agent list               # lists preconfigured agents
orch task add "Test task"    # creates task in state machine
orch tui                     # opens live dashboard
orch --version               # verifies install
```

All CLI commands in the skill are functional and verified.

## Checklist

- [x] Skill file under `skills/orch-runtime/SKILL.md`
- [x] Frontmatter with `name`, `description`, 

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
