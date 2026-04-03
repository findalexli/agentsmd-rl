# Add a one-time intro tooltip for the "go to conversation" button

## Problem

When composing a message to an existing conversation (a stream topic that already has messages, or a DM thread that already exists), the compose box shows a small arrow button that navigates to that conversation. New users don't know this button exists or what it does — there's no onboarding hint for it.

## Expected Behavior

Add a one-time introductory tooltip that appears on the "go to conversation" arrow button when a user is composing to an **existing** conversation. The tooltip should:

1. Explain what the button does (navigating to the conversation being composed to)
2. Show the keyboard shortcut (Ctrl + .)
3. Only appear once per user (register it as a `OneTimeNotice` in the onboarding steps system)
4. Only appear when composing to a conversation that already exists (check stream topic history for channel messages, and DM conversation history for direct messages)
5. Be dismissed when the user: clicks the button, cancels compose, or uses the keyboard shortcut
6. Suppress the regular hover tooltip while showing

The implementation touches both backend (registering the onboarding step) and frontend (tooltip display logic, integration with compose recipient, actions, hotkeys).

After implementing the feature, update the project's agent skill documentation (`.claude/skills/visual-test/SKILL.md`) to expand its coverage of Puppeteer testing patterns. The current SKILL.md is fairly minimal — it should be enhanced with detailed guidance on:
- Waiting patterns (waitForSelector, waitForFunction, waitForNavigation) with code examples
- Element interaction patterns (clicking, typing, hover, keyboard shortcuts)
- Navigation patterns within the app
- Reading state with page.evaluate
- Other practical patterns used in the existing test suite

## Files to Look At

- `zerver/lib/onboarding_steps.py` — where `OneTimeNotice` entries are registered
- `web/src/compose_tooltips.ts` — existing tooltip infrastructure for the compose area
- `web/src/compose_recipient.ts` — manages the "go to conversation" button visibility
- `web/src/compose_actions.ts` — compose cancel logic
- `web/src/hotkey.ts` — keyboard shortcut handling
- `web/src/onboarding_steps.ts` — frontend onboarding step management
- `.claude/skills/visual-test/SKILL.md` — agent skill documentation for visual testing
