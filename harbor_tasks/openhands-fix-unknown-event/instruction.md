# Fix "Unknown event" shown for actions with empty details

## Problem

In the OpenHands chat UI, actions that legitimately have no expandable details (like file `view` commands) are incorrectly displaying "Unknown event" instead of showing no details.

**Root cause:** The `getEventContent()` function in the frontend uses a falsy check (`details || "Unknown event"`) on the `details` return value, so an empty string `""` is treated as missing and replaced with "Unknown event".

## Files to Modify

1. `frontend/src/components/features/chat/event-content-helpers/get-event-content.tsx` - v2 UI component
2. `frontend/src/components/v1/chat/event-content-helpers/get-event-content.tsx` - v1 UI component (also needs lenient fallback for malformed events)

## Required Changes

1. **Both files**: Return `details` as-is instead of falling back to "Unknown event" when it's an empty string
2. **V1 file only**: Add a lenient fallback branch for action-like events that have an `action.kind` but fail the strict `isActionEvent()` type guard (missing `tool_name`/`tool_call_id`), so the UI shows the action kind instead of "Unknown event"

## Testing

The repo uses vitest for frontend testing. Run tests with:
```bash
cd frontend
npm run test
```

You should also verify linting and build succeed:
```bash
cd frontend
npm run lint
npm run build
```

## Success Criteria

1. The `getEventContent()` function returns empty strings as-is for `details` (not replaced with "Unknown event")
2. Action-like events with `action.kind` but missing required fields show the action kind in the title
3. All existing tests pass
4. Lint and build succeed
