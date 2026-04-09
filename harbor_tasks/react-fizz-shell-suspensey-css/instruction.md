# Suspense boundaries with suspensey CSS are incorrectly outlined during shell flush

## Problem

When React's Fizz server renderer flushes the initial shell, Suspense boundaries that only contain stylesheets with precedence (suspensey CSS) are being outlined unnecessarily. This causes a higher-level fallback to be shown (e.g., "Middle Fallback" instead of "Inner Fallback") even though the stylesheets are already emitted in the `<head>` and block paint regardless.

The `hasSuspenseyContent` function currently does not distinguish between flushing the shell and flushing a streamed completion. During shell flush, stylesheets are placed in the `<head>` which blocks paint anyway — outlining for CSS alone provides no benefit and shows the wrong fallback level.

Note that suspensey images (used for ViewTransition animation reveals) should still trigger outlining during the shell flush since their motivation is different.

## Expected Behavior

- During shell flush: boundaries with only suspensey CSS should be **inlined** (not outlined), so the innermost fallback is displayed
- During shell flush: boundaries with suspensey images should still be outlined for animation reveals
- During streamed completions: behavior should be unchanged — suspensey CSS should still cause outlining so parent content can display sooner while the stylesheet loads

## Files to Look At

- `packages/react-dom-bindings/src/server/ReactFizzConfigDOM.js` — defines `hasSuspenseyContent` which determines whether a boundary has content that requires outlining
- `packages/react-server/src/ReactFizzServer.js` — contains `flushSegment` and `flushCompletedQueues` which orchestrate the flush pipeline
- `packages/react-dom-bindings/src/server/ReactFizzConfigDOMLegacy.js` — legacy DOM config implementation of `hasSuspenseyContent`
- `packages/react-markup/src/ReactFizzConfigMarkup.js` — markup config implementation
- `packages/react-noop-renderer/src/ReactNoopServer.js` — noop renderer config implementation
