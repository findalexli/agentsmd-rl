# Mantine MCP Server Stdio Transport Fix

## Task

Fix the stdio transport in the Mantine MCP server to comply with the MCP specification.

## Problem Statement

The MCP server at `packages/@mantine/mcp-server/src/server.ts` currently uses LSP-style `Content-Length` header framing for stdio transport. This is incompatible with the MCP specification, causing MCP clients (including VS Code and other MCP-compatible editors) to hang indefinitely during the `initialize` handshake.

## Observable Symptoms

1. MCP clients hang when connecting to the server via stdio
2. The `initialize` handshake never completes
3. Clients report timeout errors when trying to communicate with the server

## Expected Behavior

The MCP specification requires that messages be sent as NDJSON (newline-delimited JSON) - one complete JSON message per line, terminated by a newline character (`\n`). The server should:

1. Read incoming messages line-by-line from stdin
2. Parse each line as a complete JSON-RPC request
3. Write outgoing messages as single-line JSON strings followed by a newline
4. Remove all Content-Length header generation and parsing code

## JSON-RPC Error Codes

The following error codes must be preserved in the implementation:
- `-32600`: Invalid Request (e.g., missing Content-Length header in the old protocol)
- `-32700`: Parse error (invalid JSON)

## File to Modify

`packages/@mantine/mcp-server/src/server.ts`

## Notes

- The fix should be minimal and focused on the protocol handling
- Existing functionality (error handling, request processing) should remain intact
- TypeScript compilation and package builds must continue to pass after the fix
