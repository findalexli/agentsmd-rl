# Reorganize MCP module into its own directory

## Problem

The Prisma CLI's MCP (Model Context Protocol) server implementation lives as a single file at `packages/cli/src/MCP.ts` alongside all other CLI commands. As the MCP feature grows, it needs its own directory for better organization.

Additionally, the local MCP server currently registers several Prisma Data Platform (PDP) tools — `Prisma-Postgres-account-status`, `Create-Prisma-Postgres-Database`, and `Prisma-Login` — that are now managed exclusively by the remote MCP server and should be removed from the local CLI server.

## Expected Behavior

1. `MCP.ts` should be moved into a new `packages/cli/src/mcp/` directory
2. All import paths referencing the old location must be updated (in `bin.ts` and within `MCP.ts` itself — relative paths change because the file is one directory deeper)
3. The three PDP-related MCP tools should be removed from the server, while keeping the core tools (migrate-status, migrate-dev, migrate-reset, Prisma-Studio)
4. Add `"MCP"` to the keywords array in `packages/cli/package.json`
5. Create a README.md in the new `mcp/` directory documenting what Prisma MCP is, how the local server works, and how to start it

## Files to Look At

- `packages/cli/src/MCP.ts` — the MCP server implementation to be moved
- `packages/cli/src/bin.ts` — imports `Mcp` from `./MCP` (needs path update)
- `packages/cli/package.json` — keywords list
