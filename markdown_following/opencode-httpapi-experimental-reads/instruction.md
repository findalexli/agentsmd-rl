# Bridge experimental read-only HttpApi endpoints

The opencode server is migrating its Hono routes to Effect's `HttpApi`
abstraction in small slices. Your job is to add the **first read-only slice**
of the experimental route group to the new HttpApi server, keep the legacy
Hono routes working, and bridge the new paths through Hono so existing
clients can hit them with the `OPENCODE_EXPERIMENTAL_HTTPAPI` flag enabled.

The repo's overall plan and conventions live in
`packages/opencode/specs/effect/http-api.md` and the package-level
`AGENTS.md`. Read those before you start — they describe how the existing
HttpApi groups (`config`, `file`, `instance`, `mcp`, …) are structured.

## Goal

Add an HttpApi group called **`experimental`** that exposes four read-only
JSON endpoints, register it with the existing HttpApi server, and bridge the
paths through the Hono `InstanceRoutes` router so they can be reached via the
existing transport.

### Endpoints

All paths are mounted under the `OPENCODE_EXPERIMENTAL_HTTPAPI` flag through
the same Hono bridge that already covers `/config`, `/file`, etc.

| Method | Path                          | Response shape                                                       |
| ------ | ----------------------------- | -------------------------------------------------------------------- |
| GET    | `/experimental/console`       | `{ consoleManagedProviders: string[], activeOrgName?: string, switchableOrgCount: number }` |
| GET    | `/experimental/console/orgs`  | `{ orgs: ConsoleOrgOption[] }`                                       |
| GET    | `/experimental/tool/ids`      | `string[]` (all registered tool IDs, including built-ins like `bash`) |
| GET    | `/experimental/resource`      | `Record<string, McpResource>` (MCP resources by name)                |

`ConsoleOrgOption` carries `accountID`, `accountEmail`, `accountUrl`, `orgID`,
`orgName`, and `active: boolean`.

`McpResource` is the existing MCP resource DTO (`name`, `uri`, optional
`description`, optional `mimeType`, `client`).

### Response semantics

- **`/experimental/console`** must return the active Console org name and the
  set of provider IDs that org manages, plus the count of orgs the user could
  switch to. When no org is logged in, `activeOrgName` is omitted entirely
  (it is an *optional key*, not a key with a `null`/empty-string value), and
  `switchableOrgCount` is `0`.
- **`/experimental/console/orgs`** must return every org the user has access
  to across logged-in accounts, with `active: true` set on the currently
  selected (account, org) pair. With no logged-in account, the array is empty.
- **`/experimental/tool/ids`** must return the IDs of every registered tool
  — both built-ins and dynamically registered ones. The built-in `bash` tool
  must appear in this list.
- **`/experimental/resource`** must return MCP resources keyed by name. With
  no MCP servers actually connected, this is an empty object `{}` (not
  `null`, not `[]`).

### Wiring requirements

- A const map of the four paths must be exported from the new HttpApi module
  under the name **`ExperimentalPaths`**, with keys `console`, `consoleOrgs`,
  `toolIDs`, `resource` set to the literal paths above. The Hono bridge
  registers passthroughs by indexing this map, so both the export name and
  the path values are part of the public contract.
- The new HttpApi must be registered with the experimental HttpApi server
  alongside the existing `ConfigApi` / `FileApi` / `InstanceApi` / `McpApi`
  / etc. groups.
- The `InstanceRoutes` Hono app must register passthrough handlers for each
  of the four paths so they reach the HttpApi handler when the experimental
  flag is on.
- Authorization must run for these endpoints the same way it does for the
  other HttpApi groups.

## MCP resource schema migration

The new HttpApi group needs a *schema* (not a zod object) describing the MCP
resource type, because HttpApi success types are Effect Schemas. Migrate
`MCP.Resource` from its current zod definition to an Effect `Schema.Struct`.

The legacy Hono route at `src/server/routes/instance/experimental.ts`
currently feeds `MCP.Resource` directly into a Hono `resolver(z.record(...))`
for SDK/OpenAPI generation. That pipeline still needs a zod schema. Your
migrated `MCP.Resource` must therefore expose a **`.zod` accessor** that
returns the equivalent zod schema, and the legacy Hono route must be updated
to use it. Other modules in this codebase already use the same `.zod`
compatibility helper for migrated schemas — follow the existing pattern.

The migrated `MCP.Resource` keeps the same field set: `name`, `uri`,
optional `description`, optional `mimeType`, `client`. Its OpenAPI identifier
must remain `McpResource`.

## Style and codebase conventions

- The package-level `AGENTS.md` is the source of truth for Effect style:
  prefer `Effect.fn("Domain.method")` for traced handlers, `Schema.Struct`
  for plain object types, `Schema.optionalKey` for *truly* optional keys
  (omitted vs. present-but-undefined), and avoid `try`/`catch`, `else`
  branches, unnecessary destructuring, and `any`.
- Per-instance state is read via `InstanceState.context`, **not** the
  `Instance.directory` / `Instance.worktree` ALS globals. If you touch a
  handler that currently reads from those globals, switch it to
  `InstanceState.context`.
- Tests live in `packages/opencode/test/` and are run with `bun test`. The
  existing `test/server/httpapi-*.test.ts` files demonstrate how to drive the
  bridged Hono router with `app().request(...)` against a tmp directory.

## Code Style Requirements

The repo runs `bun typecheck` on every package, so the codebase must
type-check end-to-end. There is no separate linter step in CI for this
slice, but follow the conventions in `AGENTS.md` and existing code:
formatting matches Prettier config (`semi: false`, `printWidth: 120`).

## How to run things locally

```
# from packages/opencode
bun typecheck
bun test --timeout 30000 test/server/httpapi-bridge.test.ts
bun test --timeout 30000 test/server/httpapi-file.test.ts
```

When the new slice is in place, the integration test for the experimental
group (provided by the harness) will exercise all four endpoints against an
empty tmp instance and assert on the response shapes described above.
