# Fix Anthropic Claude Model Token Limits + Update Agent Skills

## Problem

The model runtime has an issue where normal-context Anthropic Claude models receive an inadequate token limit, causing truncated responses. This affects models like `claude-3-5-sonnet` and `claude-3-5-haiku`.

The agent chat config has a default value that is too restrictive for tool execution results, causing unnecessary truncation.

Several agent skill documentation files in `.agents/skills/` need updates to match the latest conventions.

## Expected Behavior

When resolving max tokens for Anthropic Claude models:
- Normal-context models (those without "opus", "haiku", or "v2" in their name) should receive the higher token limit used for non-small-context models
- Small-context models (`claude-3-opus`, `claude-3-haiku`, `claude-v2`) should continue using 4096 tokens
- User-provided max_tokens values should always take priority over defaults
- Provider model maxOutput values should be respected when available
- Thinking mode settings should continue to work (enabled mode returns 32000, adaptive mode returns 64000)

The agent chat configuration should allow longer tool execution results (significantly more than the current 6000 character default).

### SKILL.md File Requirements

**Create `.agents/skills/trpc-router/SKILL.md`** documenting:
- Middleware pattern for injecting models into context
- Procedure patterns (queries and mutations)
- Router structure conventions

**Update `.agents/skills/cli/SKILL.md`** to add a section titled **"Running in Dev Mode"** that explains using `LOBEHUB_CLI_HOME=.lobehub-dev` to isolate dev credentials from the global `~/.lobehub/` directory.

Also add a section titled **"Connecting to Local Dev Server"** that documents connecting the CLI to a local development server for testing.

**Update `.agents/skills/db-migrations/SKILL.md`** to change:
- Step 4 header to exactly: **"Step 4: Update Journal Tag"**
- Content must describe updating the `tag` field in the migrations metadata journal file after renaming migration SQL files

## Scope

- Model runtime package (anthropicCompatibleFactory) — max token resolution for Claude models
- Types package agent chat config schema — toolResultMaxLength default value
- `.agents/skills/` — agent skill documentation files
