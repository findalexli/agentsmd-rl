## Bug Report: Remote Agent Host Model Picker Not Populating

### Issue Summary
When connecting to a remote agent host session, the model picker on the new session page fails to show available models. Two related issues have been identified:

### Issue 1: Models Never Populate After Authentication

In the remote agent host contribution at `src/vs/sessions/contrib/remoteAgentHost/browser/remoteAgentHost.contribution.ts`:

When a new connection is established, the remote agent host server initially reports agents with 0 models (before authentication completes). The code calls `_authenticateWithConnection()` but then immediately proceeds without waiting for authentication to complete. As a result, the models list is never updated after successful authentication.

The local agent host implementation shows the correct pattern - after authentication, it calls `refreshModels()` to trigger a root state update with the full model list. The remote agent host contribution is missing this call in both `_authenticateWithConnection` and `_authenticateAllConnections`.

### Issue 2: Model Picker Visibility Logic Issue

In the copilot session actions at `src/vs/sessions/contrib/copilotChatSessions/browser/copilotChatSessionsActions.ts`:

The `IsActiveSessionRemoteAgentHost` condition is defined but uses a hardcoded string literal instead of following the pattern used elsewhere in the file (which uses the constant from `ActiveSessionProviderIdContext`). This may cause the model picker visibility check to fail.

Additionally, the context menu bridge implementation only handles single session data, but should also support arrays for multi-select scenarios.

### Expected Behavior
- After authenticating with a remote agent host, the model picker should populate with available models
- The model picker should be visible for remote agent host sessions
- Context menu commands should work with both single and multi-select session lists

### Relevant Files
- `src/vs/sessions/contrib/remoteAgentHost/browser/remoteAgentHost.contribution.ts` - authentication and model refresh handling
- `src/vs/sessions/contrib/copilotChatSessions/browser/copilotChatSessionsActions.ts` - model picker visibility and context menu bridge

### Environment
- VS Code version: base commit at `de413b282f0b15a6618a15a79d4680b720ef9dc8`
- TypeScript codebase
