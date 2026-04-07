# Fix Agent Runtime Error Handling and Update Tracing Skill Docs

## Problem

The agent runtime's `executeStep` method in `src/server/services/agentRuntime/AgentRuntimeService.ts` has fragile error handling. When a step execution fails, the catch block makes several `await` calls to infrastructure (Redis-based `publishStreamEvent`, `loadAgentState`, `saveAgentState`, `triggerCompletionWebhook`). If any one of these operations throws (e.g., Redis ECONNRESET), the entire error handler aborts — meaning `onComplete` callbacks and webhooks never fire, leaving the operation in a stuck state.

Additionally, the `agent-tracing` CLI tool's `partial inspect` subcommand is redundant. Users should be able to inspect partial snapshots using the main `inspect` command directly, since `FileSnapshotStore.get()` should transparently fall back from completed snapshots to partials when searching by ID.

## Tasks

### 1. Make error handling in `executeStep` resilient

In the catch block of `executeStep` (around line 907 of `AgentRuntimeService.ts`), wrap each infrastructure call in its own try-catch so that a failure in one doesn't prevent the others:

- `publishStreamEvent` — catch failures, log and continue
- `loadAgentState` — catch failures, fall back to constructing a minimal error state with just `formatErrorForState(error)` and `status: 'error'`
- `saveAgentState` — catch failures, log and continue
- `triggerCompletionWebhook` — catch failures, log and continue

The `onComplete` callback call must remain outside try-catch so it always fires.

### 2. Add fallback to partials in `FileSnapshotStore.get()`

In `packages/agent-tracing/src/store/file-store.ts`, update the `get()` method to search completed snapshots first, then fall back to `this.getPartial(traceId)` if no completed snapshot matches. When a partial is found, convert it to a full `ExecutionSnapshot` using a new `partialToSnapshot()` helper that fills in defaults (`completedAt: undefined`, `completionReason: undefined`, `error: undefined`, `steps: []`, `totalSteps: 0`, `totalTokens: 0`, `totalCost: 0`, `operationId: '?'`, `traceId: '?'`, `startedAt: Date.now()`) while preserving any values the partial already provides.

### 3. Simplify the partial CLI subcommand

In `packages/agent-tracing/src/cli/partial.ts`, remove the `partial inspect` subcommand (and its `view` alias). The `partial` command should only handle `list` and `clean`. After listing partials, show a message directing users to `agent-tracing inspect <id>` to inspect them.

### 4. Update the agent-tracing skill documentation

In `.agents/skills/agent-tracing/SKILL.md`, update the "CLI Commands" section to replace the old `partial inspect` examples with the new workflow: `agent-tracing inspect <partialOperationId>` with flags like `-T` and `-p`.
