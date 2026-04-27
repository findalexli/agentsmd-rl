# feat(automated-triage): add interactive triage mode and action guard (AI-192)

Source: [monte-carlo-data/mc-agent-toolkit#54](https://github.com/monte-carlo-data/mc-agent-toolkit/pull/54)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/automated-triage/SKILL.md`

## What to add / change

## Summary

- Adds an **intent disambiguation step** so the skill correctly handles both "triage my alerts now" and "build an automated workflow" requests, rather than always pushing users toward automation
- Adds **Branch A (interactive triage)**: investigate alerts directly with triage tools, proactively offer status/severity/owner/comment actions after findings are clear, ask before executing
- Adds an **action guard for workflow mode**: write tools are blocked while building/testing a workflow to prevent accidental writes on real alerts during development
- Fixes skill description to single-line ≤250 chars per skill authoring rules; bumps version to 1.1.0

Fixes: https://linear.app/montecarlodata/issue/AI-192

## Test plan

- [x] Trigger skill with an interactive request ("triage my freshness alerts") — confirm it goes straight to Branch A without asking about workflow options
- [x] Trigger skill with an automation request ("help me build a triage workflow") — confirm it goes to Branch B with the example/adapt/scratch options
- [x] In Branch A, after assessment surfaces findings, confirm skill offers actions (status, severity, owner, comment) before executing
- [x] In Branch B, confirm write tools are not called during workflow development
- [na] Unit tests — skill is a markdown prompt file, no code to test

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
