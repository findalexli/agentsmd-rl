# Fix Budget/Credit Error Banner Disappearing Immediately

## Problem Description

When a user runs out of LLM credits, the error banner disappears almost immediately instead of remaining visible. The banner briefly shows the budget/credit error, but subsequent WebSocket events clear it within ~500ms.

## Context

The frontend's WebSocket connection handler manages real-time conversation events. Error banners are displayed using `setErrorMessage()` and cleared using `removeErrorMessage()`.

Budget/credit errors are identified by the i18n key `STATUS$ERROR_LLM_OUT_OF_CREDITS`. Each WebSocket event carries a `source` field; events originating from the LLM agent have `event.source === "agent"`.

## Bug Behavior

1. When a budget/credit error occurs, the banner shows `STATUS$ERROR_LLM_OUT_OF_CREDITS`
2. Within ~500ms, a non-error event (status update, user message, etc.) arrives
3. The event handler unconditionally calls `removeErrorMessage()`, clearing the banner
4. The `AgentErrorEvent` handling has a redundant nested `isBudgetOrCreditError(event.error)` check that sets a special i18n message — this should be simplified to just `setErrorMessage(event.error)`

## Requirements

1. Budget/credit errors (`STATUS$ERROR_LLM_OUT_OF_CREDITS`) must persist — they should NOT be cleared by non-error events
2. Budget/credit errors SHOULD be cleared when an agent event arrives (indicating the LLM is working again)
3. Non-budget errors should continue to be cleared normally on non-error events
4. The `AgentErrorEvent` handling should be simplified: call `setErrorMessage(event.error)` directly without the nested `isBudgetOrCreditError(event.error)` branch
5. All existing tests, linting, type checking, and formatting must pass

## Acceptance Criteria

The test suite verifies the fix by checking for these specific patterns in the modified source file:

- A helper function named `handleNonErrorEvent` must be present
- The condition `isBudgetError && !isAgentEvent` must appear, guarding the early return for budget error persistence
- The early return must include the comment `return; // Keep budget error visible`
- The `handleNonErrorEvent(event)` call must replace direct `removeErrorMessage()` calls in the non-error event handling paths (at least 2 call sites)
- The nested `isBudgetOrCreditError(event.error)` check combined with `setErrorMessage(I18nKey.STATUS$ERROR_LLM_OUT_OF_CREDITS)` must be removed from `AgentErrorEvent` handling sections

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier (JS/TS/JSON/Markdown formatter)`
