# Fix "Unknown event" appearing for actions with empty details

## Problem

In the chat UI, actions that legitimately have no expandable details (such as file `view` commands) are incorrectly displaying "Unknown event" text instead of showing nothing or an appropriate title.

## Affected Files

The `getEventContent()` function is located in:
- `frontend/src/components/v1/chat/event-content-helpers/get-event-content.tsx`
- `frontend/src/components/features/chat/event-content-helpers/get-event-content.tsx`

## Expected Behavior

The `getEventContent()` function returns `{ title, details }` for chat events. The expected behaviors are:

1. **Empty details handling**: When a file view action has no expandable details, the `details` field should be an empty string `""`. The current implementation may incorrectly replace empty details with a fallback value.

2. **Action-like events without strict type guard fields**: Events that have an `action` object with a `kind` field but are missing `tool_name` or `tool_call_id` should still display a meaningful title derived from the action kind, rather than showing "Unknown event".

## Verification

The repository uses vitest for frontend testing. The tests validate two specific behaviors:

- **Test 1**: "returns empty details for file view action" — a file view action event should return `details === ""`
- **Test 2**: "shows action kind for action-like events" — an event with `action.kind` but missing `tool_name`/`tool_call_id` should return `title === "FILEEDITOR"` and `details === ""`

Run the frontend tests with:
```bash
cd frontend && npm run test
```

Run linting and type checking with:
```bash
cd frontend && npm run lint
cd frontend && npm run typecheck
```

## Implementation Notes

The source code modifications should:
- Return the `details` value directly without applying a fallback when the value is an empty string
- Include a comment explaining the lenient fallback logic for action-like events that fail the strict type guard
- Handle events from the "agent" source that have an action object but are not strictly valid action events

The event-content-helpers source files should pass the repository's own linting and type checking after the fix is applied.