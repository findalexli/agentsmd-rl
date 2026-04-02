# Debug Info Exponential Accumulation in React Flight

## Problem

React's Flight client (React Server Components streaming protocol) is experiencing memory issues and potential hangs when processing deeply nested component trees. The issue appears to be in how debug info entries accumulate on outlined debug chunks during model parsing.

In development mode, when Flight resolves chunk references, debug info entries from referenced chunks are being accumulated on parent chunks. With deep component trees (e.g., 20+ levels of nested components), this accumulation becomes exponential because each outlined chunk's accumulated entries are copied to every chunk that references it. This can cause the dev server to hang and run out of memory.

## Context

The Flight client processes server-rendered React components through a streaming protocol. During this process:

1. Components can have debug info attached (ReactComponentInfo, ReactAsyncInfo, ReactIOInfo)
2. These debug info objects can reference other debug objects (owner chains, props deduplication paths)
3. The `transferReferencedDebugInfo` function propagates debug info from referenced chunks to parent chunks
4. For deep component trees with props deduplication, each level creates references to parent chunks, creating a compounding effect

The debug chunks themselves are metadata that's never rendered - they don't need debug info attached to them.

## Files to Examine

- `packages/react-client/src/ReactFlightClient.js` - Main Flight client implementation
  - Look at `initializeDebugChunk` function
  - Look at `resolveIOInfo` function
  - Look at `transferReferencedDebugInfo` usage
  - Look at `getOutlinedModel` function

## Expected Behavior

- Debug info should not accumulate exponentially on debug chunks
- References resolved during debug info resolution should not trigger debug info transfer
- Deep component trees (20+ levels) should process without memory issues

## Symptoms

- Dev server hangs when rendering deeply nested async components
- Memory usage grows exponentially with component tree depth
- The issue is particularly pronounced when props are being wrapped/modified at each level (creating deduplication references)

## Constraints

- Changes should only affect debug info handling (development mode only paths)
- The fix should not break existing debug info functionality used by React DevTools
- The fix should handle both synchronous and asynchronous resolution paths
