# Bug Report: Unhandled errors in chat widget auto-attach instructions crash the chat session

## Problem

When the chat widget attempts to automatically attach instruction files (e.g., prompt files) before sending a message, any error thrown during the computation of automatic instructions propagates unhandled up the call stack. This can cause the entire chat request submission to fail, leaving the user with a broken chat experience. The issue is particularly problematic because the auto-attach instructions feature is a non-critical enhancement — a failure there should not prevent the user from sending their message.

## Expected Behavior

If computing automatic instructions fails for any reason (e.g., a malformed prompt file, a missing resource, or an unexpected state in the tools/agents model), the error should be caught and logged, and the chat message should still be sent successfully without the automatic instructions.

## Actual Behavior

An unhandled exception during automatic instruction computation bubbles up and aborts the chat submission flow. The user's message is never sent, and no meaningful error information is logged to help diagnose the root cause.

## Files to Look At

- `src/vs/workbench/contrib/chat/browser/widget/chatWidget.ts`
