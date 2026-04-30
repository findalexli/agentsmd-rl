# Add AGENTS.md

Source: [diggerhq/opencomputer#158](https://github.com/diggerhq/opencomputer/pull/158)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Summary

Comprehensive repo guide for AI agents and developers working in this codebase.

- **Architecture**: 3-tier overview (control plane → data plane → in-VM agent) with key files for each
- **Source layout**: what lives where, what each directory owns
- **Dev loop**: 3 Makefile tiers from simplest (no DB) to distributed, exact commands
- **Environment variables**: reference table with what each does
- **Architecture boundaries**: API handlers vs domain logic, proto contracts, SDK stability, docs nav
- **CLI, deployment, database, testing**: operational reference for each
- **Managed agents context**: how sessions-api relates to this repo, what infra managed agents depend on

Follows conventions from ws-gstack, sessions-api, and demo-elasticity AGENTS.md files.

## Test plan

- [ ] Verify the Makefile commands referenced are accurate
- [ ] Verify source layout paths match current repo structure

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
