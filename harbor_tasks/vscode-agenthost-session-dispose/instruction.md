## Issue: Agent sessions disappearing from the session list unexpectedly

When a user navigates away from a chat (causing the chat session to be disposed), the corresponding backend session is also being destroyed. This causes sessions to disappear from the session list unexpectedly.

### Expected behavior
Closing or navigating away from a chat UI should NOT destroy the underlying backend session. The backend session should persist and remain in the session list.

### Actual behavior
The session vanishes from the list when the user leaves the chat. Looking at `src/vs/workbench/contrib/chat/browser/agentSessions/agentHost/`, the `AgentHostSessionHandler` class manages the lifecycle of agent sessions. When a chat session is disposed, it appears to be calling dispose methods that shouldn't be invoked.

### Steps to reproduce
1. Open an agent session in the chat UI
2. Navigate away (causing chat session disposal)
3. The session is no longer listed in the sessions view

### Files to investigate
- `src/vs/workbench/contrib/chat/browser/agentSessions/agentHost/agentHostSessionHandler.ts` — contains the session lifecycle handling
- `src/vs/workbench/contrib/chat/test/browser/agentSessions/agentHostChatContribution.test.ts` — has existing test patterns for this behavior

Please fix the session lifecycle handling so that disposing the UI chat session does not destroy the backend session.
