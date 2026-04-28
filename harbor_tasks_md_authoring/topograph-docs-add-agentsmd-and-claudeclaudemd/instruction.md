# docs: add AGENTS.md and .claude/CLAUDE.md for AI coding agents

Source: [NVIDIA/topograph#253](https://github.com/NVIDIA/topograph/pull/253)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/CLAUDE.md`
- `AGENTS.md`

## What to add / change

## Summary

Adds agent-guidance documentation following the emerging AGENTS.md convention (5-part structure: overview/architecture, setup, testing/deployment, coding conventions, PR guidelines) with topograph-specific content:

- Provider/engine boundary invariant and repository map
- Provider interface contract and new-provider checklist
- Anti-patterns and "do not change without discussion" surfaces
- DCO sign-off requirements (topograph has no org-member exemption)

\`.claude/CLAUDE.md\` is the canonical source; \`AGENTS.md\` is the public synced copy. Only the first 5 header lines differ — the bodies are byte-identical from that point.

## Context

AGENTS.md has emerged as the de facto standard for guiding AI coding agents (Codex, Cursor, Copilot, Claude Code, etc.) in OSS repositories. It pairs with Context 7 indexing as the standard agent-findability pattern.

Tracking issue: #260

## Test plan

- [x] Both files render cleanly in GitHub preview
- [x] \`cmp\` confirms the bodies match from line 6 onward
- [x] Repository map entries verified against \`ls pkg/ internal/ cmd/\`
- [x] Provider interface contract matches \`pkg/providers/providers.go:36\`
- [x] Registration pattern verified against \`pkg/registry/registry.go\`
- [x] Makefile targets verified
- [x] Coverage thresholds cited from \`codecov.yml\` (60% project / 50% patch)

## Follow-up

After this merges, the repo can be submitted to [Context 7](https://context7.com) for LLM-optimized doc indexing, closing the se

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
