#!/usr/bin/env bash
set -euo pipefail

cd /workspace/happy

# Idempotency guard
if grep -qF "3. **Add to ALL languages** - When adding new strings, you MUST add them to all " "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -19,7 +19,7 @@ This file provides guidance to Claude Code (claude.ai/code) when working with co
 - `yarn tauri:build:production` - Build production variant
 
 ### Testing
-- `yarn test` - Run tests in watch mode (Jest with jest-expo preset)
+- `yarn test` - Run tests in watch mode (Vitest)
 - No existing tests in the codebase yet
 
 ### Production
@@ -77,12 +77,13 @@ This generates `sources/changelog/changelog.json` which is used by the app.
 ## Architecture Overview
 
 ### Core Technology Stack
-- **React Native** with **Expo** SDK 53
+- **React Native** with **Expo** SDK 54
 - **TypeScript** with strict mode enabled
 - **Unistyles** for cross-platform styling with themes and breakpoints
-- **Expo Router v5** for file-based routing
+- **Expo Router v6** for file-based routing
 - **Socket.io** for real-time WebSocket communication
-- **tweetnacl** for end-to-end encryption
+- **libsodium** (via `@more-tech/react-native-libsodium`) for end-to-end encryption
+- **LiveKit** for real-time voice communication
 
 ### Project Structure
 ```
@@ -98,9 +99,10 @@ sources/
 
 1. **Authentication Flow**: QR code-based authentication using expo-camera with challenge-response mechanism
 2. **Data Synchronization**: WebSocket-based real-time sync with automatic reconnection and state management
-3. **Encryption**: End-to-end encryption using tweetnacl for all sensitive data
+3. **Encryption**: End-to-end encryption using libsodium for all sensitive data
 4. **State Management**: React Context for auth state, custom reducer for sync state
-5. **Platform-Specific Code**: Separate implementations for web vs native when needed
+5. **Real-time Voice**: LiveKit integration for voice communication sessions
+6. **Platform-Specific Code**: Separate implementations for web vs native when needed
 
 ### Development Guidelines
 
@@ -138,7 +140,7 @@ t('errors.fieldError', { field: 'Email', reason: 'Invalid format' })
 
 1. **Check existing keys first** - Always check if the string already exists in the `common` object or other sections before adding new keys
 2. **Think about context** - Consider the screen/component context when choosing the appropriate section (e.g., `settings.*`, `session.*`, `errors.*`)
-3. **Add to ALL languages** - When adding new strings, you MUST add them to all language files in `sources/text/translations/` (currently: `en`, `ru`, `pl`, `es`)
+3. **Add to ALL languages** - When adding new strings, you MUST add them to all language files in `sources/text/translations/` (currently: `en`, `ru`, `pl`, `es`, `ca`, `it`, `pt`, `ja`, `zh-Hans`)
 4. **Use descriptive key names** - Use clear, hierarchical keys like `newSession.machineOffline` rather than generic names
 5. **Language metadata** - All supported languages and their metadata are centralized in `sources/text/_all.ts`
 
PATCH

echo "Gold patch applied."
