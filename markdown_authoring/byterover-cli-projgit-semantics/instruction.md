# Proj/git semantics

Source: [campfirein/byterover-cli#338](https://github.com/campfirein/byterover-cli/pull/338)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `src/server/templates/skill/SKILL.md`

## What to add / change

## Summary

- **Problem:** SKILL.md still documented the old cloud-sync workflow (`brv push`/`brv pull`/`brv space switch`) which no longer reflects the git-based `brv vc` system.
- **Why it matters:** AI agents rely on SKILL.md to understand available commands. Outdated docs lead to agents suggesting deprecated commands or missing new capabilities like branching, merging, and local-only VC.
- **What changed:** Rewrote the "Cloud Sync" section into a comprehensive "Version Control" section covering `brv vc` — local workflow (init, status, add, commit, reset, log), branch management (branch, checkout, merge), and remote operations (remote, fetch, push, pull, clone). Updated data handling references from `brv push`/`brv pull` to `brv vc push`/`brv vc pull`.
- **What did NOT change (scope boundary):** No CLI code, tests, or runtime behavior changed. Documentation-only update.

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

- Closes ENG-1980

## Root cause (bug fixes only, otherwise write `N/A`)

N/A

## Test plan

- Coverage added:
  - [ ] Unit test
  - [ ] Integra

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
