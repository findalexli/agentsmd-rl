# Add --host CLI Option to Agent Host Server

The VS Code Agent Host server (`scripts/code-agent-host.js` and `src/vs/platform/agentHost/node/agentHostServerMain.ts`) currently only accepts a `--port` option for network binding. It always binds to `127.0.0.1` (localhost), which means it cannot be accessed from other machines on the network.

Users need a `--host` option to specify the bind address (e.g., `0.0.0.0` for all interfaces). Additionally, the server's startup message only shows a single WebSocket URL, but when binding to a wildcard address it should show both local and network URLs (similar to how Vite/webpack dev servers display URLs).

The fix should:
1. Add `--host` to the CLI argument parser in `scripts/code-agent-host.js`
2. Add `host` to `IServerOptions` in `agentHostServerMain.ts`
3. Pass the host option through to the WebSocket server creation
4. Create a `serverUrls.ts` utility that resolves local and network URLs based on the host binding
5. Update the ready message to show local and network URLs
6. Add tests for the URL resolution logic
