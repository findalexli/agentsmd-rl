# docs:[ENG-2077] add brv swarm query and brv swarm curate to SKILL

Source: [campfirein/byterover-cli#409](https://github.com/campfirein/byterover-cli/pull/409)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `src/server/templates/skill/SKILL.md`

## What to add / change

## Summary

- **Problem:** The SKILL.md template (used by the LLM agent) had no documentation for `brv swarm query`, `brv swarm curate`, or `brv swarm status`. The agent couldn't guide users on swarm memory commands.
- **Why it matters:** Without SKILL documentation, the agent doesn't know these commands exist and can't use them during conversations.
- **What changed:** Added Sections 8 (Swarm Query), 9 (Swarm Curate), and 10 (Swarm Status) to SKILL.md with command syntax, flags, sample outputs (text + JSON + explain mode), and guidance on when to use each command vs alternatives.
- **What did NOT change:** No runtime code changes. No test changes. Only documentation.

## Type of change

- [ ] Bug fix
- [ ] New feature
- [ ] Refactor (no behavior change)
- [x] Documentation
- [ ] Test
- [ ] Chore (build, dependencies, CI)

## Scope (select all touched areas)

- [ ] TUI / REPL
- [x] Agent / Tools
- [ ] LLM Providers
- [x] Server / Daemon
- [ ] Shared (constants, types, transport events)
- [ ] CLI Commands (oclif)
- [ ] Hub / Connectors
- [ ] Cloud Sync
- [ ] CI/CD / Infra

## Linked issues

- Closes ENG-2077
- Related ENG-2072, ENG-2080

## Root cause (bug fixes only, otherwise write `N/A`)

N/A

## Test plan

- Coverage added:
  - [ ] Unit test
  - [ ] Integration test
  - [x] Manual verification only
- Test file(s): N/A (documentation only)
- Key scenario(s) covered:
  - Verified all sample commands execute correctly against a con

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
