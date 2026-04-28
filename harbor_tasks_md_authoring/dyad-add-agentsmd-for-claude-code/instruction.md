# Add AGENTS.md for Claude Code, Gemini CLI and Codex

Source: [dyad-sh/dyad#1638](https://github.com/dyad-sh/dyad/pull/1638)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

Adds AGENTS.md for Claude Code, Gemini CLI and Codex.

<!-- This is an auto-generated description by cubic. -->
---
## Summary by cubic
Adds AGENTS.md with clear guidelines for working in this Electron + React repo. It standardizes IPC patterns and React/TanStack Query usage to keep code consistent and secure.

- **New Features**
  - Documents IPC architecture: renderer IpcClient, preload allowlist, host handlers, and throwing errors on failure.
  - Defines React integration: useQuery for reads, useMutation for writes, invalidate related queries, optional global state sync.
  - Notes security practices: avoid remote, validate/lock by appId on mutations.
  - Encourages descriptive names that mirror IPC channels and colocated tests/stories.

<!-- End of auto-generated description by cubic. -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
