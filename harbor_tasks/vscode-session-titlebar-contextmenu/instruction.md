# Bug Report: Session title bar context menu shows wrong icons and appears on new chat sessions

## Problem

In the VS Code sessions feature, right-clicking on the active session title in the title bar has two issues. First, the context menu appears even when the current session is a brand-new, unsaved chat session — a state where the context menu actions are not meaningful. Second, when the context menu does appear for valid sessions, the "pinned" state is always reported as `false` regardless of whether the session is actually pinned, causing the menu to display incorrect options.

Additionally, sessions originating from background (CLI) or cloud providers display incorrect icons in the session list. Instead of showing the provider-specific icon, they all fall back to the generic session icon.

## Expected Behavior

- The title bar context menu should not appear for new/unsaved chat sessions.
- The context menu should reflect the actual pinned state of the session.
- Background and cloud sessions should display their correct provider-specific icons.

## Actual Behavior

- The context menu appears on new chat sessions where it serves no purpose.
- The pinned status in the context menu is always `false`, even for pinned sessions.
- Background and cloud session types show the wrong icon.

## Files to Look At

- `src/vs/sessions/contrib/copilotChatSessions/browser/copilotChatSessionsProvider.ts`
- `src/vs/sessions/contrib/sessions/browser/sessionsTitleBarWidget.ts`
