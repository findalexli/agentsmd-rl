# feat: [ENG-2136]  add section 11 for query and curate history

Source: [campfirein/byterover-cli#445](https://github.com/campfirein/byterover-cli/pull/445)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `src/server/templates/skill/SKILL.md`

## What to add / change

Moves curate history content from section 3 into a dedicated section 11 (Query and Curate History) alongside query-log history. Adds standard Overview, Use/Do-NOT-use blocks to match the rest of SKILL.md's format.

## Summary

- Problem: Curate history commands were buried inside section 3 (Curate Context) with no dedicated home, and query-log history had no section at all.
- Why it matters: Agents following SKILL.md couldn't easily discover or reason about history inspection commands; the inconsistent structure made the skill harder to parse reliably.
- What changed: Added section 11 "Query and Curate History" with Overview, Use/Do-NOT-use blocks, and both `brv curate view` and `brv query-log view` command references. Removed the curate history block from section 3.
- What did NOT change (scope boundary): No CLI behavior, no code, no tests — documentation only.

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
- [ ] Server / Daemon
- [ ] Shared (constants, types, transport events)
- [ ] CLI Commands (oclif)
- [ ] Hub / Connectors
- [ ] Cloud Sync
- [ ] CI/CD / Infra

## Linked issues

- Closes #N/A
- Related #N/A

## Root cause (bug fixes only, otherwise write `N/A`)

N/A

## Test plan

- Coverage added:
  - [ ] Unit test
  - [ ] Inte

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
