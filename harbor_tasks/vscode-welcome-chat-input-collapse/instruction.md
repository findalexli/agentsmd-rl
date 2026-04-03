# Bug: Welcome Page Chat Input Collapses on First Keystroke

## Problem Description

In the Agent Sessions welcome page, the chat input box collapses to near-zero height immediately after the user starts typing. The input editor shrinks from its intended height (~44px) to just ~22px (or even completely invisible) after the first keystroke, making it impossible for users to see what they're typing.

## File Location

The issue is in `src/vs/workbench/contrib/welcomeAgentSessions/browser/agentSessionsWelcome.ts` in the `AgentSessionsWelcomePage` class.

## Context

The welcome page includes a chat widget for users to start new agent sessions. This widget is configured to hide the chat list area (showing only the input part). The CSS hides the list via `display: none !important`, but the underlying `ChatWidget.layout()` method still reserves `MIN_LIST_HEIGHT` (50px) for the list even when it's hidden.

With a layout height of 150px allocated for the input area, only 100px remains after the hidden list reservation. Subtracting the input chrome (toolbars, padding, attachments area totaling ~128px) leaves `_effectiveInputEditorMaxHeight` at or below zero, causing the editor to collapse.

## Expected Behavior

- The chat input should maintain a usable height (~44px or more) throughout the entire user interaction
- Users should be able to see the text they're typing
- The layout calculation should account for the fact that the list area is hidden

## What You'll Need to Do

1. Examine the `AgentSessionsWelcomePage.layoutChatWidget()` method
2. Understand how `ChatWidget.layout()` and `setInputPartMaxHeightOverride()` work
3. Fix the height calculation so the input editor doesn't collapse when the user types
4. Look at how other compact chat surfaces (like stacked chat views) handle this same problem

## Hints

- Look for similar patterns in `chatViewPane.ts` or related chat UI components
- The fix involves setting an override before calling `layout()`
- Constants like `MIN_LIST_HEIGHT` are relevant but not visible in this file directly
- The chat widget needs to know it should ignore the list height reservation

## Output

Your fix should ensure that when a user types in the welcome page chat input, the input box maintains its proper height instead of collapsing.
