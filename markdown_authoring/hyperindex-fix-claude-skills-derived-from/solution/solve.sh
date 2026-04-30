#!/usr/bin/env bash
set -euo pipefail

cd /workspace/hyperindex

# Idempotency guard
if grep -qF "**Entity relationships** \u2014 schema uses entity references; handlers use the `_id`" "packages/cli/templates/static/shared/.claude/skills/indexing-handler-syntax/SKILL.md" && grep -qF "- **Never write `pool_id: String!` in the schema when using `@derivedFrom(field:" "packages/cli/templates/static/shared/.claude/skills/indexing-schema/SKILL.md" && grep -qF "- **Entity references in schema, `_id` in handlers** \u2014 Schema uses `collection: " "packages/cli/templates/static/shared/AGENTS.md" && grep -qF "- Schema uses entity references (`collection: NftCollection!`); handlers use `_i" "packages/cli/templates/static/shared/CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/packages/cli/templates/static/shared/.claude/skills/indexing-handler-syntax/SKILL.md b/packages/cli/templates/static/shared/.claude/skills/indexing-handler-syntax/SKILL.md
@@ -105,10 +105,17 @@ const id = `${event.chainId}_${event.block.number}_${event.logIndex}`;
 ```
 This is globally unique across chains and blocks. Use it as the default unless the entity is a singleton (e.g., a Token or Pool keyed by address).
 
-**Entity relationships** — use `_id` suffix:
+**Entity relationships** — schema uses entity references; handlers use the `_id` suffix that codegen adds:
 ```ts
-// WRONG:  { token0: token0.id }
-// CORRECT: { token0_id: token0.id }
+// Schema:   token0: Token!       ← entity reference, field name is "token0"
+// Handler:  { token0_id: token0.id }  ← codegen adds _id; NEVER write "token0" here
+
+// Schema:   collection: NftCollection!
+// Handler:  { collection_id: collectionEntity.id }
+
+// WRONG:  { token0: token0.id }  ← "token0" is not a valid TypeScript field
+// WRONG:  { collection_id: String! } in schema  ← _id belongs in handlers, not schema
+// CORRECT: { token0_id: token0.id }  in handler
 ```
 
 **Optionals** — `string | undefined`, not `string | null`
diff --git a/packages/cli/templates/static/shared/.claude/skills/indexing-schema/SKILL.md b/packages/cli/templates/static/shared/.claude/skills/indexing-schema/SKILL.md
@@ -13,7 +13,8 @@ description: >-
 - Every type is an entity — **no `@entity` decorator** (unlike TheGraph)
 - Must have `id: ID!` as first field
 - Names: 1-63 chars, alphanumeric + underscore, no reserved words
-- Use `_id` suffix for relationships: `token_id: String!` not `token: Token!`
+- Relationship fields use the **entity type directly**: `collection: NftCollection!` — **never** add `_id` in the schema field name
+- The `_id` suffix only appears in TypeScript handlers (added by codegen): schema field `collection` → handler field `collection_id`
 
 ## Scalar Types
 
@@ -58,11 +59,14 @@ type Pool {
 
 type Swap {
   id: ID!
-  pool_id: String!  # the FK field
+  pool: Pool!  # entity reference — field name matches @derivedFrom "field" arg
 }
 ```
 
-The `field` argument must reference an `_id` relationship field on the derived entity.
+**Critical rules:**
+- The `field` argument must match the **schema field name** on the child entity — which is the entity reference name (`"pool"`), **not** `"pool_id"`
+- In TypeScript handlers, set this relationship using the `_id` suffix: `pool_id: poolEntity.id` — codegen transforms `pool: Pool!` → `pool_id` in the TypeScript type
+- **Never write `pool_id: String!` in the schema when using `@derivedFrom(field: "pool")`.** The schema field must be `pool: Pool!`; the `_id` is a codegen artifact for handlers only
 
 ## @index
 
@@ -121,27 +125,42 @@ enum PoolType {
   UniswapV3
 }
 
-type Pool @index(fields: ["token0_id", "token1_id"]) {
+type Token {
+  id: ID!
+  symbol: String!
+}
+
+type Pool @index(fields: ["token0", "token1"]) {
   id: ID!
   poolType: PoolType!
-  token0_id: String!
-  token1_id: String!
+  token0: Token!   # entity reference — handler uses token0_id
+  token1: Token!   # entity reference — handler uses token1_id
   reserve0: BigInt!
   reserve1: BigInt!
   totalValueLocked: BigDecimal! @config(precision: 30, scale: 15)
-  swaps: [Swap!]! @derivedFrom(field: "pool")
+  swaps: [Swap!]! @derivedFrom(field: "pool")  # "pool" matches Swap.pool field name
 }
 
 type Swap {
   id: ID!
-  pool_id: String! @index
+  pool: Pool! @index   # entity reference — handler uses pool_id; @derivedFrom field arg = "pool"
   sender: String! @index
   amount0In: BigInt!
   amount1In: BigInt!
   timestamp: BigInt! @index
 }
 ```
 
+**Schema vs handler field names:**
+
+| Schema field | Schema type | TypeScript handler field |
+|---|---|---|
+| `pool` | `Pool!` | `pool_id: string` |
+| `token0` | `Token!` | `token0_id: string` |
+| `collection` | `NftCollection!` | `collection_id: string` |
+
+Codegen always appends `_id` to entity reference field names in the TypeScript types. Do **not** add `_id` yourself in the schema.
+
 ## Deep Documentation
 
 Full reference: https://docs.envio.dev/docs/HyperIndex-LLM/hyperindex-complete
diff --git a/packages/cli/templates/static/shared/AGENTS.md b/packages/cli/templates/static/shared/AGENTS.md
@@ -30,7 +30,7 @@ pnpm test             # Run tests (Vitest)
 
 - **Spread operator for updates** — Entities returned by `context.Entity.get()` are read-only. Always spread: `context.Entity.set({ ...existing, field: newValue })`
 - **Effect API for external calls** — All `fetch`, RPC, or other async I/O must use `createEffect` + `context.effect()`. Never call external services directly in handlers.
-- **`entity_id` for relationships** — Use `token_id: String!` not `token: Token!`. No entity arrays without `@derivedFrom`.
+- **Entity references in schema, `_id` in handlers** — Schema uses `collection: NftCollection!` (entity reference, no `_id`). Handlers use `collection_id: value` (codegen adds `_id`). `@derivedFrom(field: "collection")` matches the schema field name, not the handler field name. No entity arrays without `@derivedFrom`.
 - **No `@entity` decorator** — Unlike TheGraph, schema types have no decorators.
 - **Codegen after schema/config changes** — Generated types go stale otherwise. Always `pnpm codegen` first.
 
diff --git a/packages/cli/templates/static/shared/CLAUDE.md b/packages/cli/templates/static/shared/CLAUDE.md
@@ -8,7 +8,7 @@ See `AGENTS.md` for full project context, commands, and workflow.
 - After TypeScript changes → run `pnpm tsc --noEmit`
 - Use spread operator for entity updates (returned objects are read-only)
 - Use Effect API (`createEffect` + `context.effect()`) for ALL external calls
-- Use `entity_id` fields for relationships, not entity references
+- Schema uses entity references (`collection: NftCollection!`); handlers use `_id` suffix (`collection_id: value`); never add `_id` to schema field names
 - Use pnpm, not npm
 - Run `TUI_OFF=true pnpm dev` for AI-friendly indexer output
 
PATCH

echo "Gold patch applied."
