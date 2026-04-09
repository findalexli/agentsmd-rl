# ACP session responses missing configOptions

## Problem

The ACP (Agent Client Protocol) implementation in opencode does not include `configOptions` in session responses. When ACP clients (like codecompanion) connect and create or load sessions, they receive `models` and `modes` in the response but not the `configOptions` section required by the [ACP session-config-options specification](https://agentclientprotocol.com/protocol/session-config-options). This means clients cannot discover or set configuration options like which model to use or which mode to operate in through the standardized protocol interface.

Additionally, there is no handler for the `setSessionConfigOption` RPC method, so even if a client knew about available config options, it couldn't change them through the protocol.

## Expected Behavior

- Session initialization and load responses should include a `configOptions` field containing `SessionConfigOption[]` entries for model selection and mode selection
- A `setSessionConfigOption` method should allow clients to update model and mode settings through the protocol
- The model config option should be of type `"select"` with all available models listed
- The mode config option should be of type `"select"` with all available modes listed (when modes are available)
- After setting a config option, the response should include the updated `configOptions`

## Files to Look At

- `packages/opencode/src/acp/agent.ts` — The main ACP agent implementation, handles session lifecycle and protocol methods
