# Task: Add MCP Server Shortcuts to Cline CLI

## Problem

Users currently need to manually edit `cline_mcp_settings.json` to add MCP servers. This is error-prone and inconsistent with the UI experience. A common mistake is entering a URL without specifying the transport type, which produces broken configs.

## Goal

Add a new `cline mcp add` command that lets users add MCP servers from the CLI:

```bash
# Add a stdio server
cline mcp add kanban -- kanban mcp

# Add a remote HTTP server
cline mcp add linear https://mcp.linear.app/mcp --type http
```

## Key Requirements

1. **New command structure**: Create a `mcp` command group with an `add` subcommand
2. **Transport types**: Support `stdio` (default), `http` (stored internally as `streamableHttp`), and `sse`
3. **STDIO syntax**: Use `--` separator to pass command args: `cline mcp add <name> -- <cmd> [args...]`
4. **HTTP/SSE syntax**: Single URL argument with `--type` flag
5. **URL validation**: When a URL is provided without `--type http`, show a clear error message suggesting the correct usage
6. **Config output**: Write to `~/.cline/data/settings/cline_mcp_settings.json`
7. **Schema validation**: Validate configs before writing using the project's existing schema validation
8. **Duplicate protection**: Error if a server with the same name already exists
9. **Type normalization**: Store `type: "stdio"` for stdio and `type: "streamableHttp"` for http

## Required Exports

The MCP utility module must export:
- A main async function for adding MCP servers
- An options interface for the add operation
- A result interface containing serverName, transportType, and settingsPath

## Files to Modify/Create

- `cli/src/utils/mcp.ts` - New utility module for MCP operations
- `cli/src/index.ts` - Register the mcp command with the add subcommand
- `cli/src/utils/mcp.test.ts` - Tests for the MCP utility
- `cli/src/index.test.ts` - Tests for command parsing (must include a test suite for the mcp command)

## Implementation Notes

- Use `initializeCliContext()` to resolve config directory
- Use `getMcpSettingsFilePath()` to get the settings file path
- Read existing settings with `fs.readFile`, validate, add new server, write back with `fs.writeFile`
- The settings file format: `{ mcpServers: { [name]: { command, args?, type } } }`
- For remote servers, the config must include a `url:` field
- Follow existing patterns in the codebase for CLI commands
- Use the existing color utilities (`printInfo`, `printWarning`) for output

## Validation

After implementation:
1. `npm run typecheck` should pass
2. New unit tests should pass
3. The command should correctly add both stdio and HTTP servers
4. URL without `--type` should produce a helpful error message