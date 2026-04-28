# docs(agent): codify A2A interrupt vs polling protocol

Source: [neomjs/neo#10409](https://github.com/neomjs/neo/pull/10409)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agent/skills/session-sunset/references/session-sunset-workflow.md`
- `AGENTS.md`

## What to add / change

Resolves #10408.

### Context
With the rollout of the Phase 3 Wake Substrate, multiple `[WAKE]` events can queue in the harness, leading to redundant processing loops.

### The Problem
Treating the wake text as the canonical state of the inbox breaks idempotency and causes phantom wakes. In addition, calling `mark_read` immediately upon reading breaks future-session inbox visibility.

### The Fix
This PR implements the "A2A Interrupt vs. Polling Protocol" agreed upon in session `7a2db6c6-5b4d-4870-91ea-9dfcbd4514ec`:
- Added §22.1 to `AGENTS.md`, mandating that agents treat wake text as a hardware interrupt and poll `list_messages({status: 'unread'})` as the source of truth.
- Added explicit deduplication via internal history and graceful no-ops.
- Added explicit `mark_read` execution to the `session-sunset` protocol (Option B) to preserve "hot" thread visibility during active sessions while ensuring a clean slate for the next agent session.

### Acceptance Criteria
- [x] `AGENTS.md` updated with §22.1.
- [x] `.agent/skills/session-sunset/references/session-sunset-workflow.md` updated with Step 2: Inbox Cleanup (`mark_read`).

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
