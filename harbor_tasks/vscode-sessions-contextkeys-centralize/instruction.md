# Centralize Session Context Keys

## Problem

Context key definitions for sessions are scattered across multiple files, with hardcoded string literals used in `ContextKeyExpr.equals()` calls. This pattern makes it difficult to:

1. Discover all available context keys for sessions
2. Refactor context key names safely (no IDE rename support for string literals)
3. Catch typos in context key strings at compile time

## Context

The VS Code sessions feature uses context keys extensively for UI state management. Currently:

- `IsNewChatSessionContext`, `ActiveSessionProviderIdContext`, `ActiveSessionTypeContext`, and `IsActiveSessionBackgroundProviderContext` are defined in `sessionsManagementService.ts`
- Some context keys like `chatSessionProviderId` are used as hardcoded strings in context menu overlays
- A centralized `contextkeys.ts` file already exists with some session-related context keys but is missing the active session keys

## Task

Centralize all session-related context key definitions into `src/vs/sessions/common/contextkeys.ts`, following the existing pattern established by files like `chatContextKeys.ts`.

Specifically:

1. Move context key definitions from their current scattered locations to the centralized `contextkeys.ts` file
2. Replace all hardcoded context key strings (like `'activeSessionType'`, `'chatSessionProviderId'`) with references to the `.key` property of the context key objects
3. Update imports in all consumer files to use the centralized module
4. Ensure no duplicate imports are created when merging imports

The fix should follow the architecture pattern where constants are defined once and reused, preventing string literal duplication throughout the codebase.
