# Fix Anthropic Claude Model Token Limits + Update Agent Skills

## Problem

The model runtime has an issue where normal-context Anthropic Claude models receive an inadequate token limit, causing truncated responses. This affects models like `claude-3-5-sonnet` and `claude-3-5-haiku`.

The agent chat config has a default value that is too restrictive for tool execution results, causing unnecessary truncation.

Several agent skill documentation files in `.agents/skills/` need updates to match the latest conventions.

## Expected Behavior

### Token resolution (`resolveMaxTokens`)

The async function `resolveMaxTokens` (located in the `anthropicCompatibleFactory` module of the model-runtime package, file `packages/model-runtime/src/core/anthropicCompatibleFactory/resolveMaxTokens.ts`) takes `{ max_tokens, model, providerModels, thinking? }` and returns the effective `max_tokens` value. It must satisfy:

- **Normal-context Anthropic Claude models** (those whose name does **not** contain `opus`, `haiku`, or `v2`) — must return **`64000`** when no user override or provider model is supplied. Examples: `claude-3-5-sonnet-20241022`, `claude-sonnet-4-20250514`, `claude-3-5-haiku-20241022` (note: this last one contains `haiku` in name; *however*, the small-context patterns in this codebase target only `claude-3-haiku`, `claude-3-opus`, and `claude-v2`, so `claude-3-5-haiku` is treated as normal-context and returns 64000).
- **Small-context models** matching `claude-3-opus`, `claude-3-haiku`, or `claude-v2` — must continue returning **`4096`**.
- **User-provided `max_tokens`** — must always take priority over any default. If the caller passes `max_tokens: 9999`, the function returns `9999`.
- **Provider model `maxOutput`** — when no user override is given but a matching `providerModels` entry has a `maxOutput`, that value wins. E.g. `providerModels: [{ id: 'claude-3-5-sonnet-20241022', maxOutput: 12345 }]` → returns `12345`.
- **Thinking modes** — `thinking: { type: 'enabled' }` returns **`32000`**; `thinking: { type: 'adaptive' }` returns **`64000`**.

### Tool result max length (`AgentChatConfigSchema.toolResultMaxLength`)

In `packages/types/src/agent/chatConfig.ts`, the `AgentChatConfigSchema` zod schema defines a `toolResultMaxLength` field. Its default value must be **`25000`** (raised from the previous default of `6000`). Any valid zod expression that yields a default of `25000` for this field is acceptable.

### SKILL.md File Requirements

**Create `.agents/skills/trpc-router/SKILL.md`** documenting:
- Middleware pattern for injecting models into `ctx`
- Procedure patterns (queries and mutations)
- Router structure conventions

The new file must contain the words `middleware`, `procedure`, and `router` (case-insensitive) describing TRPC conventions.

**Update `.agents/skills/cli/SKILL.md`** to add:
- A section titled exactly **"Running in Dev Mode"** that explains using `LOBEHUB_CLI_HOME=.lobehub-dev` to isolate dev credentials from the global `~/.lobehub/` directory.
- A section titled exactly **"Connecting to Local Dev Server"** that documents connecting the CLI to a local development server for testing.

Both literal section titles `Running in Dev Mode` and `Connecting to Local Dev Server` must appear in the file.

**Update `.agents/skills/db-migrations/SKILL.md`** to:
- Replace the existing Step 4 header so it reads exactly **`Step 4: Update Journal Tag`** (the file must contain the literal string `Step 4: Update Journal Tag`).
- The Step 4 body must describe updating the `tag` field in the migrations metadata journal file (so the words `tag` and `journal` appear in the section, case-insensitive) after renaming migration SQL files.

## Scope

- `packages/model-runtime/` — `anthropicCompatibleFactory` token resolution for Claude models (the `resolveMaxTokens` function).
- `packages/types/src/agent/chatConfig.ts` — `AgentChatConfigSchema.toolResultMaxLength` default value.
- `.agents/skills/` — agent skill documentation files (`trpc-router/SKILL.md`, `cli/SKILL.md`, `db-migrations/SKILL.md`).
