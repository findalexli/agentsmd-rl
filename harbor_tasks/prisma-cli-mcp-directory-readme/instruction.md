# Reorganize MCP module into its own directory

## Problem

The Prisma CLI's MCP (Model Context Protocol) server implementation lives as a single file at `packages/cli/src/MCP.ts` alongside all other CLI commands. As the MCP feature grows, it needs its own directory for better organization.

Additionally, the local MCP server currently registers several Prisma Data Platform (PDP) tools — `Prisma-Postgres-account-status`, `Create-Prisma-Postgres-Database`, and `Prisma-Login` — that are now managed exclusively by the remote MCP server and should be removed from the local CLI server.

## Expected Behavior

1. **Move MCP.ts** into a new `packages/cli/src/mcp/` directory. After the move, the original file at `packages/cli/src/MCP.ts` must no longer exist. The moved file must preserve its existing `export class Mcp` declaration and its reference to `McpServer`.

2. **Update import paths** that reference the old location:
   - In `bin.ts`: the import of `Mcp` must target `./mcp/MCP` (not `./MCP`)
   - In the moved `MCP.ts`: the file currently uses relative imports `../package.json` and `./platform/_lib/help`. After moving one directory deeper into `mcp/`, these become `../../package.json` and `../platform/_lib/help` respectively. Both resolved paths must point to files that actually exist on disk.

3. **Remove PDP tools**: the three tools `Prisma-Postgres-account-status`, `Create-Prisma-Postgres-Database`, and `Prisma-Login` must be removed from the local server's tool registrations, while keeping the core tools: `migrate-status`, `migrate-dev`, `migrate-reset`, and `Prisma-Studio`.

4. **Add keyword**: add the string `"MCP"` to the `keywords` array in `packages/cli/package.json`.

5. **Create README**: create `packages/cli/src/mcp/README.md` documenting the MCP server. The README must contain the word "MCP" (or "Model Context Protocol") and the word "Prisma" (case-insensitive matching applies).

## Files to Look At

- `packages/cli/src/MCP.ts` — the MCP server implementation to be moved
- `packages/cli/src/bin.ts` — imports `Mcp` from `./MCP` (needs path update)
- `packages/cli/package.json` — keywords list
